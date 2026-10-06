"""Explicit final snapshots stay sealed even when a sync selects that category."""
import hashlib
import json


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def finalized_for(category, root):
    path = root / 'data/finalized.json'
    return json.loads(path.read_text()).get(category) if path.exists() else None


def verify_finalized(category, root, snapshot, reviews):
    final = finalized_for(category, root)
    if final:
        if digest(snapshot) != final['snapshotHash'] or digest(reviews) != final['reviewsHash']:
            raise ValueError(f'{category} 已封榜；最终快照或复核记录发生变化，停止构建')
    return final
