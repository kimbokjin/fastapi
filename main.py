from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, File, UploadFile, Request, Response, Form
from fastapi.responses import HTMLResponse, FileResponse
from GTDB import Get_accession_number
import os
import pandas as pd
import openpyxl
from search_16S import extract_sequnece_from_genus, Mod_Sequence_file
from pathlib import Path

app = FastAPI()


app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"), name="static")


templates = Jinja2Templates(directory="/home/bokjin/fastapi/static/templates")


@ app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.post("/uploadfiles/", response_class=HTMLResponse)
async def create_upload_files(request: Request, files: UploadFile = File(...), outgroup: str = Form(None)):
    
    if outgroup:
        outgroup = outgroup.capitalize()

        if "xlsx" in files.filename:
            uploadfile = pd.read_excel(files.file, engine="openpyxl")
            uploadfile.to_excel("save_file.xlsx", index=False)
            Get_accession_number("save_file.xlsx", outgroup)
            data_result = pd.read_csv("SP_ID_list.txt")
            sp = data_result["SP_NAME"]
            id = data_result["ID"]
            result_list = []
            for i, j in zip(sp, id):
                result = {}
                result["sp"] = i
                result["id"] = j
                result_list.append(result)
    else:
        uploadfile = pd.read_excel(files.file, engine="openpyxl")
        uploadfile.to_excel("save_file.xlsx", index=False)
        Get_accession_number("save_file.xlsx", outgroup=None)
        data_result = pd.read_csv("SP_ID_list.txt")
        sp = data_result["SP_NAME"]
        id = data_result["ID"]
        result_list = []
        for i, j in zip(sp, id):
            result = {}
            result["sp"] = i
            result["id"] = j
            result_list.append(result)

    return templates.TemplateResponse("accession_result.html", {"request": request, "results": result_list})


@app.get("/result", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("result.html", {"request": request})

'''
@app.get("/hello")
async def hello(request: Request):
    data_result = pd.read_csv("SP_ID_list.txt")
    sp = data_result["SP_NAME"]
    id = data_result["ID"]
    result_list = []
    for i, j in zip(sp, id):
        result = {}
        result["sp"] = i
        result["id"] = j
        result_list.append(result)
    return templates.TemplateResponse("result.html", {"request": request, "results": result_list})
'''

@app.get("/search16S", response_class=HTMLResponse)
async def sequnce_page(request: Request):
    return templates.TemplateResponse("16S.html", {"request": request})


@app.get("/search_16s_rRNA", response_class=HTMLResponse)
async def search_16s_rRNA(request: Request):
    option = request.query_params["option"]
    target = request.query_params["target"]
    results = Mod_Sequence_file(option, target)
    return templates.TemplateResponse("16s_result.html", {"request": request, "target": target.capitalize(), "results": results})


@ app.get("/accesion_export")
async def export():
    path = "/home/bokjin/fastapi/SP_ID_list.txt"
    return FileResponse(path=path, media_type='text/txt', filename="SP_ID_list.txt")


@ app.get("/accession", response_class=HTMLResponse)
async def search_16s_rRNA(request: Request):

    return templates.TemplateResponse("accession.html", {"request": request})


@ app.get("/16s_export")
async def export():
    path = "/home/bokjin/fastapi/16S_rRNA_seq.txt"
    return FileResponse(path=path, media_type='text/txt', filename="16S_rRNA_seq.txt")
