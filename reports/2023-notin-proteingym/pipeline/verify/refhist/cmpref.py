import pandas as pd, hashlib, sys
Folder = sys.argv[1]
for c in ["1a99bd0","b11a339","151fbca","2c178ec","0406858","82b194c"]:
    d = pd.read_csv(f"{Folder}/ref_{c}.csv")
    for i in ["KCNH2_HUMAN_Kozek_2020","SCN5A_HUMAN_Glazer_2019","POLG_CXB3N_Mattenberger_2021","BRCA1_HUMAN_Findlay_2018"]:
        r = d[d.DMS_id==i].iloc[0]
        print(c, i, r.seq_len, hashlib.md5(r.target_seq.encode()).hexdigest()[:8], r.get("start_idx", "-"), r.get("DMS_total_number_mutants"))
