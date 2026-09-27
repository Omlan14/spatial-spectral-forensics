import sys; sys.path.insert(0, ".")
import numpy as np, pandas as pd
import experiments as X
from features import extract, luminance, PIXEL, FREQ
from common import ROOT
D = X.load()
# 1) alignment: recompute features for 10 random test rows from their files; labels from splits.csv
sp = pd.read_csv(ROOT/"data/splits.csv").set_index("image_id")
t = D[(D.condition=="C0")&(D.split=="test")].sample(10, random_state=0)
print("features match files:", all(np.allclose(extract(luminance(ROOT/p))[0], r[X.NAMES].values.astype(float)) for p,(_,r) in zip(t.path, t.iterrows())))
print("labels match splits:", (t.label.values == sp.loc[t.image_id].label.values).all())
# 2) shuffled-label AUROC distribution over 200 shuffles
for exp, cond, q in [("E1","C0",0),("E2","C2",None)]:
    d = D[(D.condition==cond)&((D.quality==q) if q is not None else True)].sort_values("image_id")
    tr, va, te = (d[d.split==s] for s in ("train","val","test"))
    rng = np.random.default_rng(1); a=[]
    for _ in range(200):
        sc,m,C,thr,_ = X.fit(tr, va, PIXEL+FREQ, rng.permutation(tr.y.values))
        a.append(X.auroc(te.y.values, m.decision_function(sc.transform(te[PIXEL+FREQ]))))
    a=np.array(a); print(exp, "mean %.3f sd %.3f  frac |a-.5|>.1: %.2f" % (a.mean(), a.std(), (abs(a-.5)>.1).mean()))
    # same with a random direction (no training at all)
    w = rng.standard_normal((200,14)); Z = (te[PIXEL+FREQ]-tr[PIXEL+FREQ].mean())/tr[PIXEL+FREQ].std()
    r = np.array([X.auroc(te.y.values, Z.values@wi) for wi in w]); print(exp, "random directions: mean %.3f sd %.3f" % (r.mean(), r.std()))
