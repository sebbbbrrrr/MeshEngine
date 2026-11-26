"""TripoSR geometry-only inference; upstream source is installed separately."""
import argparse, json, time, resource
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from tsr.system import TSR

def main():
    p=argparse.ArgumentParser()
    p.add_argument("image", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--resolution", type=int, default=128, choices=[64,128,256])
    p.add_argument("--device", default="cpu")
    p.add_argument("--weights", required=True, help="Local directory with trusted config.yaml and model.ckpt")
    a=p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    t=time.monotonic()
    im=Image.open(a.image).convert("RGBA")
    im.thumbnail((512,512))
    canvas=Image.new("RGBA",(max(im.size),)*2,(128,128,128,255))
    canvas.alpha_composite(im,((canvas.width-im.width)//2,(canvas.height-im.height)//2))
    im=canvas.convert("RGB")
    im.save(a.output/"input.png")
    model=TSR.from_pretrained(a.weights,config_name="config.yaml",weight_name="model.ckpt").to(a.device).eval()
    model.renderer.set_chunk_size(4096)
    loaded=time.monotonic()
    with torch.inference_mode():
        codes=model([im],device=a.device)
        inferred=time.monotonic()
        mesh=model.extract_mesh(codes,False,resolution=a.resolution)[0]
    if not len(mesh.faces) or not np.isfinite(mesh.vertices).all():
        raise RuntimeError("Invalid or empty neural mesh")
    mesh.export(a.output/"mesh.stl")
    mesh.export(a.output/"mesh.glb")
    report={"vertices":len(mesh.vertices),"faces":len(mesh.faces),"watertight":bool(mesh.is_watertight),"winding_consistent":bool(mesh.is_winding_consistent),"bounds":mesh.bounds.tolist(),"units":"normalized; not print scale","load_seconds":loaded-t,"inference_seconds":inferred-loaded,"total_seconds":time.monotonic()-t,"peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"device":a.device,"resolution":a.resolution}
    (a.output/"report.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
if __name__=="__main__": main()
