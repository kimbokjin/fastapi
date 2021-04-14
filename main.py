from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, File, UploadFile, Request, Response, Form
from fastapi.responses import HTMLResponse, FileResponse


import os
import pandas as pd
import openpyxl
from pathlib import Path
import shutil
import subprocess

from search_16S import extract_sequnece_from_genus, Mod_Sequence_file
from phylogenomic import md5sum, FastQC, SPAdes,contig_slice, get_accession_number


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
            get_accession_number("save_file.xlsx", outgroup)
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
        get_accession_number("save_file.xlsx", outgroup=None)
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


@app.get("/phylogenomic-tree/", response_class=HTMLResponse)
async def sequnce_page(request: Request):
    return templates.TemplateResponse("phylogenomic-tree.html", {"request": request})


@app.post("/pt-one/", response_class=HTMLResponse)
async def md5sumcheck(request: Request, files: List[UploadFile] = File(...)):

    md5list =[]
    filename_list =[]
    base_quality= []
    adapter = []
   
    forward_file ='forward_'+files[0].filename.replace('.gz',"")
    reverse_file = 'reverse_'+files[1].filename.replace('.gz',"")
    filename_list.append('forward_'+files[0].filename)
    filename_list.append('reverse_'+files[1].filename)
    zip_file_path_f = "/home/bokjin/fastapi/pt/input/"+forward_file
    with open(f"{zip_file_path_f}.gz", 'wb') as upload_zip:
        shutil.copyfileobj(files[0].file,upload_zip)
    zip_file_path_r = "/home/bokjin/fastapi/pt/input/"+reverse_file
    with open(f"{zip_file_path_r}.gz", 'wb') as upload_zip:
        shutil.copyfileobj(files[1].file,upload_zip)        

    path = "/home/bokjin/fastapi/pt/input"
    os.chdir(path)   

    result_1 = md5sum('forward_'+files[0].filename)
    md5list.append(result_1.decode('utf-8'))
    result_2 = md5sum('reverse_'+files[1].filename)
    md5list.append(result_2.decode('utf-8'))
    FastQC(filename_list[0],filename_list[1])
    
    return templates.TemplateResponse('pt-one.html',{'request':request,"filename": md5list})


@app.get("/pt-two/", response_class=HTMLResponse)
async def sequnce_page(request: Request):

    return templates.TemplateResponse("pt-two.html", {"request": request})


@app.get("/pt-two-result/", response_class=HTMLResponse)
async def sequnce_page(request: Request):
    path = "/home/bokjin/fastapi/pt/input"
    os.chdir(path)
    input_file=subprocess.check_output(["ls"],stdin=None,stderr=None,shell=False,timeout=None).decode('utf-8')
    input_file_list =input_file.split()
    for i in input_file_list:
        if 'forward_' in i :
            forward_file = i
        elif 'reverse_' in i :
            reverse_file = i
    limit = request.query_params["limit"]
    option1 = request.query_params["option1"]
    option2 = request.query_params["option2"]
    file_name = forward_file.replace('foward_',"")
 
    for i in range(0,len(forward_file)+1) :
        files = forward_file[0:i]
        if '.' in files :
            name = files[0:i-1]
            break
    strain_name = name.replace("forward_","")
    #SPAdes(file1 = forward_file,file2 = reverse_file,option1 = option1, option2 = option2, limit= limit)
    #contig_slice(limit,strain_name)
    return templates.TemplateResponse("pt-two-result.html", {"request": request})


@ app.get("/assembly_download")
async def export():
    path = "/home/bokjin/fastapi/pt/input"
    os.chdir(path)
    input_file=subprocess.check_output(["ls"],stdin=None,stderr=None,shell=False,timeout=None).decode('utf-8')
    input_file_list =input_file.split()
    for i in input_file_list:
        if 'forward_' in i :
            forward_file = i
    file_name = forward_file.replace('foward_',"")
 
    for i in range(0,len(forward_file)+1) :
        files = forward_file[0:i]
        if '.' in files :
            name = files[0:i-1]
            break
    strain_name = name.replace("forward_","")    
    path2 = f"/home/bokjin/fastapi/pt/gtdb_tk/{strain_name}.fna"
    return FileResponse(path=path2, media_type='text/txt', filename=f"{strain_name}.fasta")

@app.get("/pt-thr/", response_class=HTMLResponse)
async def sequnce_page(request: Request):

    return templates.TemplateResponse("pt-thr.html", {"request": request})

@app.post("/pt_uploadfiles/", response_class=HTMLResponse)
async def create_upload_files(request: Request, files: UploadFile = File(...), outgroup: str = Form(None)):
    path = "/home/bokjin/fastapi/pt/input"
    os.chdir(path)    
    if outgroup:
        outgroup = outgroup.capitalize()

        if "xlsx" in files.filename:
            uploadfile = pd.read_excel(files.file, engine="openpyxl")
            uploadfile.to_excel("save_file.xlsx", index=False)
            get_accession_number("save_file.xlsx", outgroup)
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
        uploadfile = pd.read_csv(files.file)
        uploadfile.to_csv("save_file.csv", index=False)
        get_accession_number("save_file.csv", outgroup=None)
        data_result = pd.read_csv("SP_ID_list.txt")
        sp = data_result["SP_NAME"]
        id = data_result["ID"]
        result_list = []
        for i, j in zip(sp, id):
            result = {}
            result["sp"] = i
            result["id"] = j
            result_list.append(result)

    return templates.TemplateResponse("pt-thr.html", {"request": request, "results": result_list})    