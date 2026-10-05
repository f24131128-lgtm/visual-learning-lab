"""Three deterministic sources sharing one contract; never imported by production."""
import math
from analogy.schema import VERSION
from source_atlas.model import semantic_catalog
from scene.world.validator import normalize_world
from world_fixtures import base, representation


def formal(kind):
    if kind=="queue":
        return None,{"fifo":dict(label="先進先出佇列",pages=[1],kind="concept_map",equation="",representations=[])}
    if kind=="electricity":
        scene=base("歐姆定律 V = IR",[("volts","電壓","V",1.,10.,5.,.1),("ohms","電阻","Ω",1.,10.,2.,.1)],
            [("voltage","電壓","V","volts"),("resistance","電阻","Ω","ohms"),("current","電流","A","volts/ohms"),("zero","原點","","0")])
        scene["axes"].update(x_min=-1.,x_max=12.,y_min=-1.,y_max=12.)
        representation(scene,"objects","current_point","電流","current",["zero","current"],"point")
        representation(scene,"series","current_series","定電壓下的電流","current",["current"])
        for i,label in (("voltage","電壓"),("resistance","電阻"),("current","電流")): representation(scene,"metrics","metric_"+i,label,i,[i])
    else:
        scene=base("正弦波與相位",[("phase","相位","rad",-math.pi,math.pi,0.,.05)],
            [("angle","相位角","rad","phase+time"),("wave","正弦訊號","","sin(angle)"),("horizontal","水平投影","","cos(angle)")])
        scene["time"].update(max=2*math.pi)
        representation(scene,"objects","pointer","旋轉指針","angle",["horizontal","wave"],"vector")
        representation(scene,"series","waveform","訊號","wave",["wave"])
        representation(scene,"metrics","wave_value","訊號值","wave",["wave"])
    scene=normalize_world(scene,[1])
    return scene,semantic_catalog(scene)


def primitive(identifier,entity,kind,label,**kw):
    result=dict(id=identifier,entity_id=entity,type=kind,label=label,x="0",y="0",x2="1",y2="1",radius="0.15",value="0",visible="1",count=1,color="blue",control_parameter="",wrap_x=False,wrap_min=0.,wrap_max=1.)
    result.update(kw)
    return result


def parameter(identifier,label,low,high,default,mapping,target="",step=.1):
    return dict(id=identifier,label=label,unit="",min=low,max=high,default=default,step=step,mapping_id=mapping,formal_target=target,scale=1.,offset=0.)


def spec(kind):
    formal_ids={"electricity":["voltage","resistance","current"],"phase":["angle","wave"],"queue":["fifo"]}[kind]
    analogy_ids={"electricity":["head","restriction","flow"],"phase":["clock","projection"],"queue":["people"]}[kind]
    labels={"head":"水位差","restriction":"管道限制","flow":"水流","clock":"旋轉指針","projection":"指針投影","people":"排隊的人"}
    result=dict(version=VERSION,suitable=True,reason="有明確且有限的對應。",title={"electricity":"水流與電路","phase":"旋轉指針與正弦波","queue":"排隊與先進先出"}[kind],learning_goal="觀察同一個關係在兩種模型中的表現。",formal_focus=formal_ids[0],analogy_domain=kind,explanation="使用可調整的教學模型理解來源概念。",
        candidates=[dict(id="candidate_one",title="可互動的有限譬喻",clarity=.9,visualizability=.9,interaction=.9,fidelity=.8,misconception_risk=.2)],selected_candidate="candidate_one",
        formal_entities=[dict(id=i,source_pages=[1]) for i in formal_ids],analogy_entities=[dict(id=i,label=labels[i]) for i in analogy_ids],
        mappings=[dict(id="map_"+a,formal_id=f,analogy_id=a,relationship="對應的是關係，不是物理上的同一事物。",explains=labels[a]+"幫助觀察來源概念的變化。",fidelity=.8,mode="qualitative" if kind=="queue" else "quantitative") for f,a in zip(formal_ids,analogy_ids)],
        limitations=[dict(breaks={"electricity":"水流不等於電子運動；此簡化模型不描述交流、電磁場或實際水力損失。","phase":"指針只是相位的幾何表示，並不代表訊號由實體指針產生。","queue":"排隊只顯示先進先出順序，不描述並行排程或優先權佇列。"}[kind],misconception="不要把譬喻中的物件視為正式模型的物理實體。")],parameters=[],quantities=[],time=dict(duration=6.,frames=80),primitives=[],annotations=[])
    if kind=="electricity":
        result["parameters"]=[parameter("level","水位差",1.,10.,5.,"map_head","world:volts"),parameter("tightness","管道限制",1.,10.,2.,"map_restriction","world:ohms")]
        result["quantities"]=[dict(id="speed",expression="level/tightness"),dict(id="width",expression=".25+1/tightness")]
        result["primitives"]=[
            primitive("tank","head","rectangle","水位差",x="-2",y="level/5",x2="1.2",y2="level/2.5",control_parameter="level"),
            primitive("pipe","restriction","rectangle","管道限制",x="2",y="0",x2="6",y2="width",color="orange",control_parameter="tightness"),
            primitive("water","flow","tokens","水流",x="speed*time+index*.7",y=".1*sin(index)",radius=".1",count=8,wrap_x=True,wrap_min=-1.,wrap_max=5.),
            primitive("flow_meter","flow","meter","相對流量",x="-2",y="-1.5",value="speed")]
    elif kind=="phase":
        result["parameters"]=[parameter("offset","指針起始相位",-math.pi,math.pi,0.,"map_clock","world:phase",step=.05)]
        result["quantities"]=[dict(id="theta",expression="time+offset")]
        result["primitives"]=[primitive("hand","clock","segment","旋轉指針",x2="cos(theta)",y2="sin(theta)",control_parameter="offset"),
            primitive("tip","clock","disc","指針端點",x="cos(theta)",y="sin(theta)",radius=".12"),
            primitive("signal","projection","curve","正弦投影",x="2+time",y="sin(theta)",color="orange"),
            primitive("wave_meter","projection","meter","目前投影",x="2",y="-1.5",value="sin(theta)")]
    else:
        result["parameters"]=[parameter("amount","排隊人數",1.,8.,4.,"map_people",step=1.)]
        result["primitives"]=[primitive("line","people","tokens","排隊順序（左端為隊首）",x="index",y="0",radius=".3",count=8,visible="amount-index-.5",control_parameter="amount"),
            primitive("order","people","disc","依先進先出順序查看",x="(amount-1)*time/6",y="-1",radius=".2",color="orange")]
        result["annotations"]=[dict(entity_id="people",text="橘色標記依序查看隊首到隊尾；不是出隊速度或優先權模型。")]
    return result
