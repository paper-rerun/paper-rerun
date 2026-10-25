# Checks every downloaded file against the server: size + git blob sha1 from the GitHub tree API
# (COMP6 @ 79f41c15, matgl @ v1.3.0), and for the weights also size + sha256 from the Hugging Face LFS listing.
# Stdlib only. Writes data/verify_manifest.json
import hashlib
import json
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path("/mnt/e/Ciencia/pipeline/2025-ko-matgl")
DATA = ROOT / "data"
COMP6_COMMIT = "79f41c156f8e19506fe951b5513b98e7c534a503"
MATGL_COMMIT = "a6ebaebd6a0021e14d49d001103508c4980d94da"
MODELS = {"M3GNet": "M3GNet-PES-ANI-1x-Subset", "SO3Net": "SO3Net-PES-ANI-1x-Subset", "TensorNet": "TensorNet-PES-ANI-1x-Subset"}


def GetJson(Url):
	Request = urllib.request.Request(Url, headers={"User-Agent": "repro-check"})
	with urllib.request.urlopen(Request, timeout=60) as Response:
		return json.load(Response)


def HashFile(FilePath):
	Content = FilePath.read_bytes()
	GitSha1 = hashlib.sha1(b"blob %d\0" % len(Content) + Content).hexdigest()
	Sha256 = hashlib.sha256(Content).hexdigest()
	return len(Content), GitSha1, Sha256


Manifest = []
AllOk = True

# COMP6 test files
Comp6Tree = GetJson(f"https://api.github.com/repos/isayev/COMP6/git/trees/{COMP6_COMMIT}?recursive=1")
Comp6Blobs = {Entry["path"]: Entry for Entry in Comp6Tree["tree"] if Entry["type"] == "blob" and Entry["path"].endswith(".h5")}
for ServerPath, Entry in sorted(Comp6Blobs.items()):
	LocalPath = DATA / ServerPath
	if not LocalPath.exists():
		Manifest.append({"file": ServerPath, "status": "not downloaded", "server_size": Entry["size"]})
		continue
	Size, GitSha1, Sha256 = HashFile(LocalPath)
	bOk = Size == Entry["size"] and GitSha1 == Entry["sha"]
	AllOk = AllOk and bOk
	Manifest.append({"file": str(LocalPath.relative_to(ROOT)), "source": f"github isayev/COMP6@{COMP6_COMMIT[:8]}:{ServerPath}",
		"size": Size, "server_size": Entry["size"], "git_blob": GitSha1, "server_git_blob": Entry["sha"], "sha256": Sha256, "ok": bOk})

# Weights: copy from the v1.3.0 checkout into data/weights, check against GitHub tree at the tag and against Hugging Face
MatglTree = GetJson(f"https://api.github.com/repos/materialyzeai/matgl/git/trees/{MATGL_COMMIT}?recursive=1")
MatglBlobs = {Entry["path"]: Entry for Entry in MatglTree["tree"] if Entry["type"] == "blob"}
for ModelName, HfRepo in MODELS.items():
	FolderName = f"{ModelName}-ANI-1x-Subset-PES"
	HfFiles = {Entry["path"]: Entry for Entry in GetJson(f"https://huggingface.co/api/models/materialyze/{HfRepo}/tree/main")}
	for FileName in ["model.json", "model.pt", "state.pt", "README.md"]:
		ServerPath = f"pretrained_models/{FolderName}/{FileName}"
		if ServerPath not in MatglBlobs:
			continue
		SourcePath = ROOT / "repo" / ServerPath
		LocalPath = DATA / "weights" / FolderName / FileName
		LocalPath.parent.mkdir(parents=True, exist_ok=True)
		shutil.copyfile(SourcePath, LocalPath)
		Size, GitSha1, Sha256 = HashFile(LocalPath)
		Entry = MatglBlobs[ServerPath]
		bOk = Size == Entry["size"] and GitSha1 == Entry["sha"]
		AllOk = AllOk and bOk
		Row = {"file": str(LocalPath.relative_to(ROOT)), "source": f"github materialyzeai/matgl@v1.3.0:{ServerPath}",
			"size": Size, "server_size": Entry["size"], "git_blob": GitSha1, "server_git_blob": Entry["sha"], "sha256": Sha256, "ok": bOk}
		# Hugging Face copy, informational: LFS files carry sha256, small files carry the git blob sha1
		HfEntry = HfFiles.get(FileName)
		if HfEntry:
			if "lfs" in HfEntry:
				Row["hf_match"] = HfEntry["lfs"]["oid"] == Sha256 and HfEntry["size"] == Size
			else:
				Row["hf_match"] = HfEntry["oid"] == GitSha1
		Manifest.append(Row)

(DATA / "verify_manifest.json").write_text(json.dumps(Manifest, indent=1))
for Row in Manifest:
	print(Row.get("ok"), Row.get("hf_match", "-"), Row.get("size"), Row.get("server_size"), Row["file"])
print("ALL OK" if AllOk else "MISMATCH")
sys.exit(0 if AllOk else 1)
