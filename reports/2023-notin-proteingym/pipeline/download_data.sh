#!/bin/bash
# Download test data, authors' scores and ESM weights, then verify size (+ S3 multipart md5 for the weights, zip CRC for the zips)
# Restartable: curl resumes partial files, verified files are skipped
set -u
D=/mnt/e/Ciencia/pipeline/2023-notin-proteingym/data
mkdir -p "$D/weights"
PG=https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3
FB=https://dl.fbaipublicfiles.com/fair-esm/models

# name|url|size|s3etag (empty when the server has no checksum)
LIST="
DMS_ProteinGym_substitutions.zip|$PG/DMS_ProteinGym_substitutions.zip|43021128|
zero_shot_substitutions_scores.zip|$PG/zero_shot_substitutions_scores.zip|1911045703|
weights/esm2_t6_8M_UR50D.pt|$FB/esm2_t6_8M_UR50D.pt|30099493|27cdd93dc0dc3b242e2e7edd237963fe-4
weights/esm2_t12_35M_UR50D.pt|$FB/esm2_t12_35M_UR50D.pt|134095705|57bed9af0d55e6235f9093b9d1f5cb60-16
weights/esm2_t30_150M_UR50D.pt|$FB/esm2_t30_150M_UR50D.pt|592774773|94352f3f0532130916af68983d51f3ea-71
weights/esm2_t33_650M_UR50D.pt|$FB/esm2_t33_650M_UR50D.pt|2604537549|12a18098227c0ff911354647d25d494d-311
weights/esm1b_t33_650M_UR50S.pt|$FB/esm1b_t33_650M_UR50S.pt|7828576466|80558ee238433d05fafc92b4a447b41d-934
"

# S3 multipart ETag: md5 of the concatenated binary md5 of each 8 MiB part, plus -<parts>
s3etag() {
	python3 - "$1" <<'PY'
import hashlib, sys
PartSize = 8 * 1024 * 1024
PartDigests = b""
PartCount = 0
with open(sys.argv[1], "rb") as File:
	while True:
		Chunk = File.read(PartSize)
		if not Chunk:
			break
		PartDigests += hashlib.md5(Chunk).digest()
		PartCount += 1
print(hashlib.md5(PartDigests).hexdigest() + "-" + str(PartCount))
PY
}

echo "$LIST" | while IFS='|' read -r Name Url Size Etag; do
	[ -z "$Name" ] && continue
	# Optional filter so the slow server and the fast one can run in parallel
	case "$Name" in ${1:-*}) ;; *) continue ;; esac
	F="$D/$Name"
	if [ -f "$F.verified" ]; then
		echo "skip $Name (verified)"
		continue
	fi
	curl -sSfL -C - --retry 5 --retry-delay 10 -o "$F" "$Url" || echo "curl failed for $Name"
	Got=$(stat -c %s "$F" 2>/dev/null || echo 0)
	if [ "$Got" != "$Size" ]; then
		echo "FAIL size $Name: got $Got expected $Size"
		continue
	fi
	Check="size ok"
	if [ -n "$Etag" ]; then
		Mine=$(s3etag "$F")
		if [ "$Mine" != "$Etag" ]; then
			echo "FAIL etag $Name: got $Mine expected $Etag"
			continue
		fi
		Check="$Check, s3 etag ok"
	fi
	case "$Name" in
		*.zip)
			if unzip -tq "$F" > "$F.ziptest.log" 2>&1; then
				Check="$Check, zip crc ok"
			else
				echo "FAIL zip crc $Name"
				continue
			fi
			;;
	esac
	Sha=$(sha256sum "$F" | cut -d' ' -f1)
	echo "$Name $Size $Sha ($Check)" | tee "$F.verified"
done

# Unpack the substitution assays and only the ESM score folders from the authors' scores
cd "$D"
if [ -f DMS_ProteinGym_substitutions.zip.verified ] && [ ! -d DMS_ProteinGym_substitutions ]; then
	unzip -q DMS_ProteinGym_substitutions.zip
fi
if [ -f zero_shot_substitutions_scores.zip.verified ] && [ ! -d zero_shot_substitutions_scores/ESM1b ]; then
	unzip -q -o zero_shot_substitutions_scores.zip 'zero_shot_substitutions_scores/ESM1b/*' 'zero_shot_substitutions_scores/ESM2/8M/*' 'zero_shot_substitutions_scores/ESM2/35M/*' 'zero_shot_substitutions_scores/ESM2/150M/*' 'zero_shot_substitutions_scores/ESM2/650M/*' || echo "unzip of scores failed"
fi
cat "$D"/*.verified "$D"/weights/*.verified 2>/dev/null > "$D/VERIFIED.txt"
echo "done"
