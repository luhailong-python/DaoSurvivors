"""Preserve evidence for an actually completed host imagegen call; no generation."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('name');ap.add_argument('image');ap.add_argument('--transparent',action='store_true');a=ap.parse_args()
    p=(ROOT/a.image).resolve();p.relative_to(ROOT)
    receipt=ROOT/'docs/production'/f'{a.name}.receipt.json'
    r=json.loads(receipt.read_text(encoding='utf-8'))
    cfg=json.loads(Path('F:/work/image/config/image-generation.json').read_text(encoding='utf-8'))
    refs=[]
    for f in r['submitted']['references']:
        q=Path(f);im=Image.open(q)
        refs.append({'file':str(q),'sha256':sha(q),'dimensions':list(im.size),'role':'identity and/or art style reference actually attached'})
    im=Image.open(p)
    when=datetime.fromisoformat(r['finished'].replace('Z','+00:00')).isoformat()
    parameters={'promptFile':f'docs/production/{a.name}.prompt.txt','referenced_image_paths':r['submitted']['references'],'transparent_background':a.transparent,'model':None,'quality':None}
    d={'schemaVersion':1,'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'generatedAt':when,'generationStartedAt':r['submitted']['started'],'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'alphaExtrema':im.getchannel('A').getextrema() if im.mode=='RGBA' else None,'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','operation':'native model output; byte-for-byte copy from host generated_images directory','configSnapshot':cfg,'submittedParameters':parameters,'actualModel':None,'actualQuality':None,'estimateUsd':None,'unverifiedReason':'宿主管理；image_gen工具没有model/quality选择器，结果没有可靠的实际型号/质量元数据；不能以配置或提示词作为证明。内置入口未披露逐图成本。','evidence':{'receipt':receipt.relative_to(ROOT).as_posix(),'returnedOutputHint':r.get('output_hint'),'sourceToolResultKeys':['image_url','output_hint']},'prompt':parameters['promptFile'],'references':refs,'unityIntegration':'not-performed'}
    p.with_suffix(p.suffix+'.generation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'file':d['file'],'size':im.size,'sha256':d['sha256'],'generationRecord':str(p.with_suffix(p.suffix+'.generation.json'))},ensure_ascii=False))
if __name__=='__main__':main()
