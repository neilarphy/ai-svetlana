import logging
from os import path, makedirs, listdir
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from ..schemas.document import GenerateRequest
from ..services import generation
import yaml

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Generator"]
)

BASE_DIR = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
DOCS_DIR = path.join(BASE_DIR, 'generated_docs')
makedirs(DOCS_DIR, exist_ok=True)

MASTER_PROMPT_PATH = path.join(BASE_DIR, 'master_prompt.md')

MASTER_PROMPT = ""
try:
    with open(MASTER_PROMPT_PATH, 'r', encoding='utf-8') as f:
        MASTER_PROMPT = f.read()
except FileNotFoundError:
    print("CRITICAL ERROR: master_prompt.md not found!")


@router.post("/generate")
async def generate_document(request: GenerateRequest):
    if not MASTER_PROMPT:
        raise HTTPException(status_code=500, detail="Server error: Master prompt not loaded.")

    generated_yaml_str = generation.generate_yaml_from_gpt(MASTER_PROMPT, request)
    logger.info(f"AI Model Response:\n{generated_yaml_str}")
    if not generated_yaml_str:
        raise HTTPException(status_code=500, detail="Failed to generate content from AI model.")

    try:
        data = yaml.safe_load(generated_yaml_str)
    except yaml.YAMLError:
        raise HTTPException(status_code=500, detail="Failed to parse YAML from AI model.")

    base_filename = str(uuid.uuid4())
    yaml_log_filename = f"{base_filename}.yaml"
    yaml_log_path = path.join(DOCS_DIR, yaml_log_filename)
    try:
        with open(yaml_log_path, 'w', encoding='utf-8') as f:
            f.write(generated_yaml_str)
    except IOError as e:
        logger.error(f"Failed to log YAML response: {e}")

    # HACK/FIX: вручную смерджить ямл в ответ, чтобы получить все поля
    if request.sender:
        if 'sender' not in data or not data['sender']:
            data['sender'] = {}
        data['sender']['name'] = data['sender'].get('name', request.sender.name)
        data['sender']['position'] = data['sender'].get('position', request.sender.position)

    if request.recipient:
        if 'recipient' not in data or not data['recipient']:
            data['recipient'] = {}
        data['recipient']['name'] = data['recipient'].get('name', request.recipient.name)
        data['recipient']['position'] = data['recipient'].get('position', request.recipient.position)


    doc_type_request = request.document_type.replace('_', ' ').lower()
    template_name = ""
    if doc_type_request == "служебная записка":
        template_name = "sluzhebnaya_zapiska.docx"
    elif doc_type_request == "письмо":
        template_name = "pismo.docx"
    # HACK: заглушка для фикса фронта
    elif doc_type_request in ["приказ", "заявление", "протокол", "докладная записка"]:
        # заглушка для других типов
        template_name = "pismo.docx" 
    else:
        raise HTTPException(status_code=400, detail=f"Unknown document type: {request.document_type}")

    data["document_type"] = doc_type_request.capitalize()

    file_stream = generation.fill_docx_template(template_name, data)
    
    doc_filename = f"{base_filename}.docx"
    meta_filename = f"{base_filename}.json"
    
    doc_file_path = path.join(DOCS_DIR, doc_filename)
    meta_file_path = path.join(DOCS_DIR, meta_filename)
    
    with open(doc_file_path, "wb") as f:
        f.write(file_stream.getbuffer())

    now = datetime.now()
    timestamp = now.strftime('%Y%m%d_%H%M%S')

    def sanitize(name):
        if not name: return ""
        return "".join(c for c in name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')

    sender_name = sanitize(request.sender.name)
    recipient_name = ""
    if request.recipient:
        recipient_name = sanitize(request.recipient.name)
    elif request.recipients:
        recipient_name = sanitize(request.recipients[0].name) 

    subject_line = sanitize(request.subject)

    name_parts = [
        timestamp,
        request.document_type,
        sender_name,
        recipient_name,
        subject_line
    ]
    display_name = "_".join(filter(None, name_parts)) + ".docx"
    
    metadata = {
        "doc_filename": doc_filename,
        "display_name": display_name,
        "document_type": doc_type_request.capitalize(),
        "created_at": now.isoformat()
    }
    with open(meta_file_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    return JSONResponse(content=metadata)

@router.get("/documents")
async def get_documents():
    documents_data = []
    for filename in sorted(listdir(DOCS_DIR), reverse=True):
        if filename.endswith(".json"):
            meta_path = path.join(DOCS_DIR, filename)
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    documents_data.append(json.load(f))
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Could not read or parse metadata file {filename}: {e}")
    return documents_data

@router.get("/download/{filename}")
async def download_document(filename: str):
    doc_path = path.join(DOCS_DIR, filename)
    meta_path = path.join(DOCS_DIR, filename.replace(".docx", ".json"))

    if not path.exists(doc_path):
        raise HTTPException(status_code=404, detail="File not found")

    display_name = filename
    if path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                display_name = metadata.get("display_name", filename)
        except (IOError, json.JSONDecodeError):
            pass 

    return FileResponse(
        path=doc_path, 
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
        filename=display_name
    )

@router.get("/templates")
async def get_templates():
    templates_dir = path.join(BASE_DIR, 'templates')
    templates = []
    for filename in listdir(templates_dir):
        if filename.endswith(".docx"):
            templates.append(filename)
    return templates
