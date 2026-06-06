# Resume and JD Manual Test Checklist

Use this checklist with the backend running at `http://127.0.0.1:8000` and the frontend running at `http://localhost:5173`.

- [ ] Resume TXT upload works
- [ ] Resume PDF upload works if possible with a non-private sample PDF
- [ ] JD pasted text save works
- [ ] JD file upload works
- [ ] Context refresh works
- [ ] Clear context works
- [ ] Generate cues uses saved context
- [ ] Unsupported file type fails cleanly
- [ ] Frontend build passes with `npm run build`
- [ ] Backend still starts

## PDF Manual Test Notes

Use only a fake or non-private PDF. Upload it through the Resume file input or JD file input. A text-based PDF should return a filename, character count, and preview. An image-only scanned PDF may fail or return no text until OCR is added.
