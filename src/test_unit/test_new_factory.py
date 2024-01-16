from pyuppaal.nta import Location, Edge, Template


def test_location():
    """load location from xml string.
    """
    # =================== 第1个测试 ======================
    txt1 = """<location id="id1" x="0" y="0">
			<name x="-10" y="-34">location_name</name>
			<label kind="invariant" x="-10" y="17">inv_inv</label>
			<label kind="exponentialrate" x="-10" y="34">1.9</label>
			<label kind="testcodeEnter">on_enter_on_enter</label>
			<label kind="testcodeExit">on_exit_on_exit</label>
			<label kind="comments" x="-10" y="59">comments_comments</label>
			<committed/>
		</location>
    """
    l1 = Location.from_xml(txt1)
    
    simplified_l1_text = l1.xml.replace("\n", "").replace(" ", "")
    simplified_txt1 = txt1.replace("\n", "").replace("\t", "").replace(" ", "")
    assert simplified_l1_text == simplified_txt1, f"\nsimplified_l1_text=\n{simplified_l1_text}\nsimplified_txt1=\n{simplified_txt1}"
    
    # 人工构造l1的实例
    l1_instance = Location(location_id=1, 
                           location_pos=(0, 0),
                           name="location_name",
                           name_pos=(-10, -34),
                           invariant="inv_inv",
                           invariant_pos=(-10, 17),
                           rate_of_exponential=1.9,
                           rate_of_exp_pos=(-10, 34),
                           is_initial=False,
                           is_committed=True,
                           is_urgent=False,
                           comments="comments_comments",
                           comments_pos=(-10, 59),
                           test_code_on_enter="on_enter_on_enter",
                           test_code_on_exit="on_exit_on_exit")
    simplified_l1_instance_text = l1_instance.xml.replace("\n", "").replace(" ", "")
    assert simplified_l1_text == simplified_l1_instance_text, f"\nsimplified_l1_text=\n{simplified_l1_text}\nsimplified_l1_instance_text=\n{simplified_l1_instance_text}"
    
    # =================== 第2个测试: 没有 name, 没有 exp ======================
    txt2 = """<location id="id1" x="0" y="0">
                <label kind="invariant" x="-10" y="17">inv_inv</label>
                <label kind="testcodeEnter">on_enter_on_enter</label>
                <label kind="testcodeExit">on_exit_on_exit</label>
                <label kind="comments" x="-10" y="59">comments_comments</label>
                <committed/>
            </location>
    """
    
    l2 = Location.from_xml(txt2)
    simplified_l2_text = l2.xml.replace("\n", "").replace(" ", "")
    simplified_txt2 = txt2.replace("\n", "").replace("\t", "").replace(" ", "")
    assert simplified_l2_text == simplified_txt2, f"\nsimplified_l2_text=\n{simplified_l2_text}\nsimplified_txt2=\n{simplified_txt2}"
    
    # 人工构造l2的实例
    l2_instance = Location(location_id=1, 
                           location_pos=(0, 0),
                           name_pos=(-10, -34),
                           invariant="inv_inv",
                           invariant_pos=(-10, 17),
                           # rate_of_exponential=0.5,
                           # rate_of_exp_pos=(-10, 34),
                           is_initial=False,
                           is_committed=True,
                           is_urgent=False,
                           comments="comments_comments",
                           comments_pos=(-10, 59),
                           test_code_on_enter="on_enter_on_enter",
                           test_code_on_exit="on_exit_on_exit")
    simplified_l2_instance_text = l2_instance.xml.replace("\n", "").replace(" ", "")
    assert simplified_l2_text == simplified_l2_instance_text, f"\nsimplified_l2_text=\n{simplified_l2_text}\nsimplified_l2_instance_text=\n{simplified_l2_instance_text}"
     
def test_branch_point():
    txt = """<branchpoint id="id6" x="-119" y="-144">
		</branchpoint>"""
    
    bp = Location.from_xml(txt)
    simplified_bp_txt = bp.xml.replace("\n", "").replace(" ", "")
    simplified_txt = txt.replace("\n", "").replace("\t", "").replace(" ", "")
    assert simplified_bp_txt == simplified_txt, f"\nsimplified_bp_txt=\n{simplified_bp_txt}\nsimplified_txt=\n{simplified_txt}"
    
    # 人工构造branch_point的实例
    bp_instance = Location(location_id=6, location_pos=(-119, -144), is_branchpoint=True)
    simplified_bp_instance_txt = bp_instance.xml.replace("\n", "").replace(" ", "")
    assert simplified_bp_txt == simplified_bp_instance_txt, f"\nsimplified_bp_txt=\n{simplified_bp_txt}\nsimplified_bp_instance_txt=\n{simplified_bp_instance_txt}"
    
def test_edge():
    # =================== 第1个测试: 普通边 ======================
    txt_normal = """<transition>
		 	<source ref="id1"/>
		 	<target ref="id2"/>
		 	<label kind="select" x="18" y="-51">nnn:id</label>
			<label kind="guard" x="18" y="-34">guard:=0</label>
		 	<label kind="synchronisation" x="18" y="-17">sync?</label>
		 	<label kind="assignment" x="18" y="0">update</label>
		 	<label kind="testcode">testcode_testcode</label>
		 	<label kind="comments" x="18" y="25">comments_comments</label>
		 	<nail x="51" y="42"/>
		 	<nail x="76" y="34"/>
		 </transition>"""
    e_normal = Edge.from_xml(txt_normal)
    simplified_e_normal_txt = e_normal.xml.replace("\n", "").replace(" ", "")
    simplified_normal_txt = txt_normal.replace("\n", "").replace("\t", "").replace(" ", "")
    assert simplified_normal_txt == simplified_e_normal_txt, f"\nsimplified_normal_txt=\n{simplified_normal_txt}\nsimplified_e_normal_txt=\n{simplified_e_normal_txt}"
    
    # 人工构造normal edge的实例
    e_normal_instance = Edge(source_location_id=1, target_location_id=2,
                             source_location_pos=(-1, -1), target_location_pos=(-1, -1),
                             select="nnn:id",
                             select_pos=(18, -51),
                             sync="sync?",
                             sync_pos=(18, -17),
                             update="update",
                             update_pos=(18, 0),
                             guard="guard:=0",
                             guard_pos=(18, -34),
                             probability_weight=None,
                             prob_weight_pos=None,
                             comments="comments_comments",
                             comments_pos=(18, 25),
                             test_code="testcode_testcode",
                             nails=[(51, 42), (76, 34)])
    simplified_e_normal_instance_txt = e_normal_instance.xml.replace("\n", "").replace(" ", "")
    assert simplified_normal_txt == simplified_e_normal_instance_txt, f"\nsimplified_e_normal_txt=\n{simplified_e_normal_txt}\nsimplified_e_normal_instance_txt=\n{simplified_e_normal_instance_txt}"
    
    # =================== 第2个测试: 概率边 ======================
    txt_prob = """<transition>
			<source ref="id11"/>
			<target ref="id8"/>
			<label kind="synchronisation" x="-305" y="-80">param1!</label>
			<label kind="probability" x="-305" y="-51">0.8</label>
		</transition>"""
    e_prob = Edge.from_xml(txt_prob)
    simplified_e_prob_txt = e_prob.xml.replace("\n", "").replace(" ", "")
    simplified_prob_txt = txt_prob.replace("\n", "").replace("\t", "").replace(" ", "")
    assert simplified_e_prob_txt == simplified_prob_txt, f"\nsimplified_e_prob_txt=\n{simplified_e_prob_txt}\nsimplified_prob_txt=\n{simplified_prob_txt}"

    # 人工构造 probability edge的实例
    e_prob_instance = Edge(source_location_id=11, target_location_id=8,
                            source_location_pos=(-1, -1), target_location_pos=(-1, -1),
                            sync="param1!",
                            sync_pos=(-305, -80),
                            update=None,
                            update_pos=None,
                            guard=None,
                            guard_pos=None,
                            probability_weight=0.8,
                            prob_weight_pos=(-305, -51),
                            comments=None,
                            comments_pos=None,
                            test_code=None,
                            nails=[])
    simplified_e_prob_instance_txt = e_prob_instance.xml.replace("\n", "").replace(" ", "")
    assert simplified_prob_txt == simplified_e_prob_instance_txt, f"\nsimplified_prob_txt=\n{simplified_prob_txt}\n=\n{simplified_e_prob_instance_txt}"


# ================== 关于 Template 基础功能的测试(xml, from_xml) =================

def test_template():
    # ==================Test 1：==============================
    txt_temp = """<template>
            <name>Receiver</name>
            <parameter>broadcast chan &amp;param1, broadcast chan &amp;param2, int inv_start, int guard_start</parameter>
            <declaration>// Place local declarations here.
    clock t;</declaration>
            <location id="id0" x="-391" y="-102">
                <name x="-401" y="-136">Start</name>
                <label kind="invariant" x="-401" y="-85">t&lt;=inv_start</label>
                <label kind="testcodeEnter">count ++;</label>
                <label kind="testcodeExit">count = 10;</label>
            </location>
            <location id="id1" x="-178" y="-102">
                <label kind="invariant" x="-188" y="-85">t&lt;=200</label>
                <label kind="exponentialrate" x="-187" y="-93">0.8</label>
            </location>
            <location id="id2" x="-42" y="-93">
                <urgent/>
            </location>
            <location id="id3" x="-76" y="-212">
                <committed/>
            </location>
            <location id="id4" x="25" y="-212">
                <name x="15" y="-246">End1</name>
            </location>
            <location id="id5" x="34" y="-93">
                <name x="24" y="-127">End2</name>
                <label kind="comments" x="25" y="-34">备注End2</label>
            </location>
            <branchpoint id="id6" x="-119" y="-144">
            </branchpoint>
            <init ref="id0"/>
            <transition>
                <source ref="id2"/>
                <target ref="id5"/>
                <label kind="synchronisation" x="-24" y="-110">param2?</label>
                <label kind="assignment" x="-24" y="-93">t=888</label>
            </transition>
            <transition>
                <source ref="id3"/>
                <target ref="id4"/>
                <label kind="synchronisation" x="-58" y="-229">param1?</label>
                <label kind="assignment" x="-51" y="-212">t=999</label>
            </transition>
            <transition>
                <source ref="id6"/>
                <target ref="id3"/>
                <label kind="probability" x="-93" y="-178">0.2</label>
            </transition>
            <transition>
                <source ref="id6"/>
                <target ref="id2"/>
                <label kind="probability" x="-93" y="-119">0.8</label>
            </transition>
            <transition>
                <source ref="id1"/>
                <target ref="id6"/>
            </transition>
            <transition>
                <source ref="id0"/>
                <target ref="id1"/>
                <label kind="guard" x="-331" y="-102">t&gt;= guard_start</label>
                <label kind="assignment" x="-306" y="-85">count ++</label>
                <label kind="testcode">count == -1;</label>
            </transition>
        </template>
    """
    temp_from_xml = Template.from_xml(txt_temp)
    simplified_temp_txt = temp_from_xml.xml.replace("\n", "").replace(" ", "")
    simplified_txt = txt_temp.replace("\n", "").replace("\t", "").replace(" ", "")
    assert simplified_temp_txt == simplified_txt, f"simplified_txt=\n{simplified_txt}\nsimplified_temp_txt=\n{simplified_temp_txt}"
