/**
 * Prediction Report PDF Download Utility
 * Provides multi-tiered resilient PDF export:
 * 1. Backend ReportLab high-precision vector PDF
 * 2. Backend on-the-fly export for in-memory streaming reports
 * 3. Client-side html2pdf fallback
 */

export async function downloadPredictionReportPdf({
  reportId,
  reportOutline,
  generatedSections,
  fallbackElement
} = {}) {
  const rId = reportId && reportId !== 'REF-2024-X92' ? reportId : null

  const saveBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  const cleanTitle = (reportOutline?.title || rId || 'Prediction_Report')
    .replace(/[^\w\-_.]/g, '_')
    .substring(0, 60)
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '')
  const defaultFilename = `${cleanTitle || 'Prediction_Report'}.pdf`

  // Tier 1: Download existing report PDF from backend
  if (rId) {
    try {
      const res = await fetch(`/api/report/${encodeURIComponent(rId)}/download?format=pdf`)
      if (res.ok) {
        let filename = defaultFilename
        const disposition = res.headers.get('Content-Disposition')
        if (disposition && disposition.includes('filename=')) {
          const match = disposition.match(/filename=(?:["']?)(.*?)(?:["']?)(?:;|$)/)
          if (match && match[1]) filename = match[1]
        }
        const blob = await res.blob()
        saveBlob(blob, filename)
        return true
      }
    } catch (err) {
      console.warn('Direct PDF download error, trying export endpoint:', err)
    }
  }

  // Tier 2: Export in-memory report payload via backend
  try {
    const res = await fetch('/api/report/export-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        report_id: rId || 'report_preview',
        outline: reportOutline || {},
        sections_content: generatedSections || {},
        created_at: new Date().toISOString()
      })
    })
    if (res.ok) {
      const blob = await res.blob()
      saveBlob(blob, defaultFilename)
      return true
    }
  } catch (err) {
    console.warn('Backend export-pdf endpoint failed, trying html2pdf fallback:', err)
  }

  // Tier 3: Client-side html2pdf fallback
  const el = fallbackElement || document.querySelector('.report-content-wrapper')
  if (el) {
    try {
      const html2pdfModule = await import('html2pdf.js')
      const html2pdf = html2pdfModule.default || html2pdfModule
      const opt = {
        margin: [10, 10, 10, 10],
        filename: defaultFilename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, backgroundColor: '#000000' },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      }
      await html2pdf().set(opt).from(el).save()
      return true
    } catch (err) {
      console.error('html2pdf generation failed:', err)
      throw err
    }
  }

  throw new Error('No content available for PDF generation')
}
