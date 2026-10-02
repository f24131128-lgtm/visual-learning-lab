"""Original deterministic source diagrams; never imported by production."""

import math

import pymupdf

from source_atlas.schema import VERSION


def region(identifier, page, box, label, semantic, kind="vector", layer="vectors", confidence="high", excerpt=""):
    return dict(region_id=identifier, page=page, bbox=dict(zip(("x0", "y0", "x1", "y1"), box)) if box else None,
        type=kind, label=label, semantic_ids=semantic, source_text_excerpt=excerpt,
        parent_region_id=None, related_region_ids=[], layer=layer, grounding_note="", confidence=confidence)


def atlas_fixture(system="phasor"):
    if system == "phasor":
        regions = [
            region("formula_a", 1, (.07,.06,.94,.16), "Phase A formula", ["ia"], "formula", "formulas", excerpt="Ia(t) = A cos(2 pi f t)"),
            region("wave_a", 1, (.08,.20,.94,.43), "Three-phase waveforms", ["ia", "ib", "ic"], "graph_region", "structure"),
            region("vector_b", 1, (.23,.46,.52,.7), "Phase B phasor", ["ib"]),
            region("label_b", 1, (.19,.46,.38,.52), "Phase B label", ["ib"], "label", "labels"),
            region("formula_b", 2, (.08,.08,.95,.2), "Phase B formula", ["ib"], "formula", "formulas", excerpt="Ib(t) = A cos(2 pi f t - 2 pi/3)"),
            region("uncertain", 2, (.1,.4,.9,.8), "Messy annotation", ["ib"], "annotation", "relationships", "low"),
        ]
        regions[2]["related_region_ids"] = ["label_b", "formula_b"]
    else:
        regions = [
            region("position_formula", 1, (.07,.06,.95,.16), "Horizontal position formula", ["px"], "formula", "formulas", excerpt="x(t) = v0 cos(theta) t"),
            region("trajectory", 1, (.08,.22,.94,.75), "Flight path", ["px", "py"], "diagram", "structure"),
            region("velocity_arrow", 1, (.35,.31,.58,.48), "Velocity arrow", ["vx", "vy"]),
            region("velocity_label", 1, (.57,.3,.78,.37), "Velocity label", ["vx"], "label", "labels"),
            region("velocity_formula", 2, (.07,.08,.95,.2), "Velocity components", ["vx", "vy"], "formula", "formulas", excerpt="vx = v0 cos(theta)"),
        ]
    return dict(atlas_version=VERSION, processed_pages=[1,2], regions=regions)


def source_pdf(system="phasor"):
    """Unequal original pages, visual arrows + formulas + graph, not AI output."""
    with pymupdf.open() as doc:
        p = doc.new_page(width=600,height=700)
        formula = "Ia(t) = A cos(2 pi f t)" if system == "phasor" else "x(t) = v0 cos(theta) t"
        p.insert_text((48,80), formula, fontsize=19)
        if system == "phasor":
            for phase,color in enumerate(((.7,.2,.3),(.2,.5,.8),(.3,.65,.35))):
                points = [pymupdf.Point(50+500*i/100,210-55*math.cos(i*2*math.pi/100-phase*2*math.pi/3)) for i in range(101)]
                shape = p.new_shape(); shape.draw_polyline(points); shape.finish(color=color,width=2); shape.commit()
            p.draw_line((55,280),(565,280),color=(.4,.4,.4))
            center=(310,480)
            for phase in range(3):
                angle = phase*2*math.pi/3
                end=(center[0]+130*math.cos(angle), center[1]-130*math.sin(angle))
                p.draw_line(center,end,color=(.25,.4,.7),width=3)
                p.draw_circle(end,4,color=(.25,.4,.7),fill=(.25,.4,.7))
            p.insert_text((120,352),"Phase B",fontsize=17)
        else:
            points=[pymupdf.Point(60+490*i/100,500-225*4*(i/100)*(1-i/100)) for i in range(101)]
            shape=p.new_shape();shape.draw_polyline(points);shape.finish(color=(.3,.3,.8),width=3);shape.commit()
            p.draw_line((60,505),(565,505),color=(.4,.4,.4))
            p.draw_line((215,320),(340,245),color=(.2,.5,.8),width=4)
            p.draw_circle((340,245),5,fill=(.2,.5,.8))
            p.insert_text((345,240),"velocity",fontsize=17)
        p = doc.new_page(width=800,height=500)
        p.insert_text((64,70),"Ib(t) = A cos(2 pi f t - 2 pi/3)" if system == "phasor" else "vx = v0 cos(theta)", fontsize=20)
        # Deliberately ambiguous visual marks: a low-confidence anchor, no fake box.
        for n in range(8): p.draw_line((100+n*35,240+n*5),(400+n*20,290-n*7),color=(.4,.4,.4))
        return doc.tobytes()


def page_texts(pdf):
    with pymupdf.open(stream=pdf,filetype="pdf") as doc:
        return {n+1:p.get_text() for n,p in enumerate(doc)}
