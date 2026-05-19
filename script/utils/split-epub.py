#!/usr/bin/env python3
"""Split manga EPUB into two halves. Direct approach: keep spine order, split at midpoint."""

import zipfile, os, shutil, re

SRC = "/home/kita/Documents/book/[零落].epub"
OUT_DIR = "/home/kita/Documents/book"
TMP = "/home/kita/Documents/book/epub_split"

if os.path.exists(TMP):
    shutil.rmtree(TMP)

with zipfile.ZipFile(SRC, 'r') as z:
    z.extractall(TMP)

with open(os.path.join(TMP, "item", "standard.opf"), 'r', encoding='utf-8') as f:
    opf_text = f.read()

# Get all spine refs in order
spine_refs = re.findall(r'<itemref idref="([^"]+)"', opf_text)
print(f"Spine items: {len(spine_refs)}")

split_at = len(spine_refs) // 2

# Map from ref_id to (xhtml_filename, page_number)
page_map = {}  # ref_id -> (xhtml_file, page_num_or_none)
for ref_id in spine_refs:
    m = re.search(r'<item[^>]*id="' + re.escape(ref_id) + r'"[^>]*href="([^"]+)"', opf_text)
    if m:
        href = m.group(1)
        fname = os.path.basename(href)
        pnum = None
        p_m = re.search(r'p-(\d+)', fname)
        if p_m:
            pnum = int(p_m.group(1))
        page_map[ref_id] = (fname, pnum)

# Collect all image filenames from manifest
all_images = set(re.findall(r'image/(i-\d+\.png)', opf_text))

for suffix, start, end in [('_pt1', 0, split_at), ('_pt2', split_at, len(spine_refs))]:
    part_ids = set(spine_refs[start:end])
    part_out = os.path.join(OUT_DIR, f"[零落]{suffix}.epub")
    
    needed_xhtml_fnames = set()
    needed_img_ids = set()
    needed_img_fnames = set()
    page_nums = set()
    
    for ref_id in part_ids:
        if ref_id in page_map:
            fname, pnum = page_map[ref_id]
            needed_xhtml_fnames.add(fname)
            if pnum is not None:
                page_nums.add(pnum)
                needed_img_fnames.add(f"i-{pnum:03d}.png")
    
    # Also include cover image
    needed_img_fnames.add("i-000.png")
    needed_xhtml_fnames.add("p-cover.xhtml")
    
    # Build new OPF text
    new_opf_lines = []
    in_manifest = False
    in_spine = False
    in_metadata = True
    
    for line in opf_text.split('\n'):
        stripped = line.strip()
        
        if '<metadata' in stripped:
            in_metadata = True
        elif '</metadata>' in stripped:
            in_metadata = False
        elif '<manifest>' in stripped:
            in_manifest = True
        elif '</manifest>' in stripped:
            in_manifest = False
        elif '<spine>' in stripped:
            in_spine = True
        elif '</spine>' in stripped:
            in_spine = False
        
        if in_manifest:
            # Check if this item is needed
            id_m = re.search(r'id="([^"]+)"', stripped)
            href_m = re.search(r'href="([^"]+)"', stripped)
            
            if id_m:
                item_id = id_m.group(1)
                
                # Keep if in our page set or is cover
                keep = False
                if item_id in part_ids:
                    keep = True
                elif item_id == 'cover':
                    keep = True
                elif item_id.startswith('i-'):
                    # Check if this image is needed
                    img_fname = None
                    if href_m:
                        img_fname = os.path.basename(href_m.group(1))
                    else:
                        # Try to determine from fallback
                        fallback_m = re.search(r'fallback="([^"]+)"', stripped)
                        # Can't determine easily, skip
                    
                    if img_fname and img_fname in needed_img_fnames:
                        keep = True
                    # Also check the id numbering
                    id_num_m = re.search(r'i-(\d+)', item_id)
                    if id_num_m and int(id_num_m.group(1)) in page_nums:
                        keep = True
                    # Keep image 0 (cover image)
                    if item_id in ('i-000', 'i-001') or 'i-000' in needed_img_fnames:
                        if 'i-000.png' in needed_img_fnames:
                            keep = True
                
                # Keep CSS and other non-page resources
                if href_m and not href_m.group(1).startswith('xhtml/'):
                    if not href_m.group(1).startswith('image/'):
                        keep = True
                
                if not keep:
                    continue
            else:
                # No id, keep it (shouldn't happen but be safe)
                pass
        
        if in_spine:
            id_m = re.search(r'idref="([^"]+)"', stripped)
            if id_m and id_m.group(1) not in part_ids:
                continue
        
        new_opf_lines.append(line)
    
    new_opf_text = '\n'.join(new_opf_lines)
    
    # Build EPUB
    with zipfile.ZipFile(part_out, 'w', zipfile.ZIP_DEFLATED) as zout:
        # mimetype first, uncompressed
        zout.write(os.path.join(TMP, 'mimetype'), 'mimetype', compress_type=zipfile.ZIP_STORED)
        
        for root_dir, dirs, files in os.walk(TMP):
            for fname in files:
                fpath = os.path.join(root_dir, fname)
                arcname = os.path.relpath(fpath, TMP)
                
                if arcname.startswith('META-INF/'):
                    zout.write(fpath, arcname)
                    continue
                if arcname == 'mimetype':
                    continue
                
                # Filter xhtml
                if arcname.startswith('item/xhtml/'):
                    if fname in needed_xhtml_fnames:
                        zout.write(fpath, arcname)
                    continue
                
                # Filter images
                if arcname.startswith('item/image/'):
                    if fname in needed_img_fnames:
                        zout.write(fpath, arcname)
                    continue
                
                # Write modified OPF
                if arcname == 'item/standard.opf':
                    zout.writestr(arcname, new_opf_text)
                    continue
                
                # Write everything else
                zout.write(fpath, arcname)
    
    size_mb = os.path.getsize(part_out) / 1024 / 1024
    print(f"{suffix}: {len(needed_xhtml_fnames)} XHTML, ~{len(needed_img_fnames)} images, {size_mb:.1f} MB")

shutil.rmtree(TMP)
print("Done!")
