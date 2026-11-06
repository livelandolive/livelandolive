import copy, sys, json, docx
from docx.shared import Pt
from docx.oxml.ns import qn

def set_cell(cell, text, bold=False, size=10):
    cell.text = ""
    lines = text.split("\n")
    p = cell.paragraphs[0]
    for i, line in enumerate(lines):
        if i > 0:
            p = cell.add_paragraph()
        r = p.add_run(line)
        r.bold = bold
        r.font.size = Pt(size)

def build(spec_path, out_path, template="매매일지_양식.docx"):
    spec = json.load(open(spec_path, encoding="utf-8"))
    d = docx.Document(template)
    body = d.element.body
    paras = d.paragraphs
    tables = d.tables
    # header
    set_cell(tables[0].rows[0].cells[1], spec["지부"])
    set_cell(tables[0].rows[0].cells[3], spec["이름"])
    # title
    t = paras[1]
    for r in t.runs[1:]: r.text = ""
    t.runs[0].text = spec["제목"]
    # block elements: P3, T1, T2, P5, T3, T4
    blk = [paras[3]._p, tables[1]._tbl, tables[2]._tbl, paras[5]._p, tables[3]._tbl, tables[4]._tbl]
    anchor = paras[2]._p
    # summary paragraph(s) after header
    insert_after = anchor
    for line in spec.get("요약", []):
        np = copy.deepcopy(paras[2]._p)
        insert_after.addnext(np); insert_after = np
        para = docx.text.paragraph.Paragraph(np, paras[2]._parent)
        run = para.add_run(line); run.font.size = Pt(10)
        if line.startswith("■"): run.bold = True
    # clone block per trade
    last = blk[-1]
    clones = []
    for tr in spec["거래"]:
        new = [copy.deepcopy(e) for e in blk]
        sep = copy.deepcopy(paras[2]._p)
        last.addnext(sep); cur = sep
        for e in new:
            cur.addnext(e); cur = e
        last = cur
        clones.append((tr, new))
    for e in blk: body.remove(e)
    for tr, new in clones:
        p_side = docx.text.paragraph.Paragraph(new[0], paras[3]._parent)
        for r in p_side.runs: r.text = ""
        side = tr["구분"]
        for word in ["매수", " / ", "매도"]:
            run = p_side.add_run(word); run.bold = (word.strip() == side)
            if word.strip() == side: run.font.size = Pt(12)
        t1 = docx.table.Table(new[1], d._body); t2 = docx.table.Table(new[2], d._body)
        t3 = docx.table.Table(new[4], d._body); t4 = docx.table.Table(new[5], d._body)
        set_cell(t1.rows[0].cells[1], tr["종목명"], bold=True); set_cell(t1.rows[0].cells[3], tr["매매일자"])
        set_cell(t2.rows[0].cells[1], tr["단가"]); set_cell(t2.rows[0].cells[3], tr["수량"])
        set_cell(t2.rows[1].cells[1], tr["총매매액"]); set_cell(t2.rows[1].cells[3], tr.get("평단가","-"))
        set_cell(t2.rows[2].cells[1], tr.get("실현손익","-")); set_cell(t2.rows[2].cells[3], tr.get("수익률","-"))
        set_cell(t3.rows[0].cells[0], "차트 (캡쳐 후 붙여넣기)\n" + tr.get("차트메모","(키움 앱 일봉 차트 캡처를 여기에 붙여넣기)"))
        set_cell(t4.rows[0].cells[0], "메모\n" + tr["메모"], size=9)
        set_cell(t4.rows[0].cells[1], "참고한 뉴스\n" + tr["뉴스"], size=9)
        p5 = docx.text.paragraph.Paragraph(new[3], paras[5]._parent)
        for r in p5.runs: r.text = ""
    d.save(out_path)

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
