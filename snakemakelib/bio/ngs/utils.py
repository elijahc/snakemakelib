# Copyright (C) 2015 by Per Unneberg
import re
from snakemakelib.config import get_sml_config
from snakemakelib.utils import isoformat

sml_config = get_sml_config()

def read_group_from_str(s):
    """Generate read group values from a string.

    Tries to guess sensible values from string.

    Args: 
      s: <string> to be parsed

    Returns:
      d: <dict> of read group key:value mappings
    """
    ngs_cfg = get_sml_config('bio.ngs.settings')
    m = re.match(ngs_cfg['run_id_re'][1], s)
    d = {k:None for k in ngs_cfg['read_group_keys']}
    d.update({k:v for (k,v) in (zip(ngs_cfg['run_id_re'][0], m.groups())) if not k=="_"})
    d['date'] = isoformat(d['date'])
    if "center" in list(d):
        d["center"] = ngs_cfg.get('center', "")
    if "platform" in list(d):
        d["platform"] = ngs_cfg.get('platform', "")
    if "description" in list(d):
        d["description"] = s
    if "id" in list(d):
        d["id"] = s
    return d
