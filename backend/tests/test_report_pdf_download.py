import pytest
from app import create_app
from app.services.report_pdf_generator import ReportPDFGenerator


def test_report_pdf_generator_basic():
    report_data = {
        'report_id': 'test_report_001',
        'outline': {
            'title': 'Test Prediction Report',
            'summary': 'Summary of predictions and outcomes.',
            'sections': [
                {'title': 'First Findings', 'content': 'Section content with **bold** and *italic*.'}
            ]
        },
        'created_at': '2026-10-24 02:00:00'
    }
    pdf_bytes = ReportPDFGenerator.generate_pdf(report_data)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b'%PDF-')


def test_report_pdf_download_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.get('/api/report/report_754cee5cfe50/download?format=pdf')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'
    assert b'%PDF-' in response.data[:20]


def test_report_pdf_export_endpoint():
    app = create_app()
    client = app.test_client()

    payload = {
        'report_id': 'export_test_001',
        'outline': {
            'title': 'Export Endpoint Test',
            'summary': 'Testing export endpoint functionality.',
            'sections': [
                {'title': 'Section Alpha', 'content': 'Testing inline markdown.'}
            ]
        }
    }
    response = client.post('/api/report/export-pdf', json=payload)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'
    assert b'%PDF-' in response.data[:20]
