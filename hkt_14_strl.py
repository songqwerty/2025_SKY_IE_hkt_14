import streamlit as st

st.set_page_config(
    page_title="가젤"
)

import time
import random
from crawling import crawling

a_for_M = 60 
a_for_C = 25
a_for_L = 40 #카테고리 변경에 따른 변수 수정(수정 확인 후 주석 지워주세요)
x = []
I = []
run = False
# 페이지 설정

# 타이틀
col_t, col_blank = st.columns([99, 1])
with col_t:
    st.markdown("<h1 style='text-align:center;font-size:55px;'>마감 기한이 있는 시험기간 </h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:right;font-size:18px;'>10일 벼락치기 for 좋은 학점 + 낮은 스트레스 지수</p>", unsafe_allow_html=True)

# 컬럼 설정
schedule_tab, timer_tab = st.tabs(["최적 시간표", "타이머"])

if 'gurobi_results' not in st.session_state:
    st.session_state.gurobi_results = None



# 왼쪽: 최적 시간표
with schedule_tab:
    with st.container(border=True):
        
        if 'crawling_done' not in st.session_state:
            st.session_state.crawling_done = False
            st.session_state.results = {} 
            st.session_state.timer_end_time = None

        st.markdown("<h3 style='color:#E74C3C;'>SNULife 로그인</h3>", unsafe_allow_html=True)
        st.markdown("---")

        #아이디, 비번 입력받기
        space1, middle, space2 = st.columns([1,2,1])    
        with middle:
            sub_col1, sub_col2 = st.columns(2) # 3칸에서 2칸으로 수정

            with sub_col1:
                user_id = st.text_input("snulife_id : ",value = None, placeholder='\t') #아이디
                st.session_state.user_id = user_id
            with sub_col2:
                user_pw = st.text_input('snulife_pw : ',type = 'password', value = None, placeholder= '\t')#비번
                st.session_state.user_pw = user_pw
    
    with st.container(border=True):
        st.markdown("<h3 style='color:#E74C3C;'>내 시험 과목 입력하기</h3>", unsafe_allow_html=True)
        st.markdown("---")
        key_word_1 = st.text_input('이번 학기에 어떤 것 수강?',value = None, placeholder = '쉼표로 구분해서 입력!')
        user_id = st.session_state.user_id ; user_pw = st.session_state.user_pw
        run_1 = st.button("당도 측정 시작!", use_container_width = True) #멘트 수정 

        if run_1:
            if user_id and user_pw and key_word_1:
                subjects_list = [s.strip() for s in key_word_1.split(',')]
                key_word = ','.join(subjects_list)
                with st.spinner('잘 익은 과일을 수확하려면 오래걸려요..'): #멘트 수정
                    crawler = crawling(user_id,user_pw,key_word)
                    if crawler.login():
                        sorted_subject = crawler.sorting()
                        sorted_credit = crawler.subject_credit()
                        sweetness_subject = crawler.crawl_start()
                    else:
                        st.error("""
                            <div style="text-align: center; font-size: 28px; font-weight: bold;">
                                아이디, 비번 다시 입력하세요!
                            </div>
                        """, icon="🚨")
                    st.session_state.crawling_done = True
                    st.session_state.results = {
                            "sorted_dict": sorted_subject,
                            "credits": sorted_credit,
                            "sweetness": sweetness_subject
                        }
            else:
                st.error('모두 다 입력해야 실행됩니다!')

        


if st.session_state.crawling_done:
    results = st.session_state.results
    results['combined'] = sum(results['sorted_dict'].values(),[])
    combined_list = results['combined']

# 왼쪽: 최적 시간표
if st.session_state.crawling_done:
    with schedule_tab:
        with st.container(border=True):
            #시험 과목 설정하기
            st.markdown("<h3 style='color:#E74C3C;'>내 능력치 평가하기 </h3>", unsafe_allow_html=True)
            st.markdown("---")
    
            ability_M = None;
            ability_L = None;
            ability_C = None
    
            M_options = [s.strip() for s in results['sorted_dict'].get('memorize', [])]
            C_options = [s.strip() for s in results['sorted_dict'].get('math', [])]
            L_options = [s.strip() for s in results['sorted_dict'].get('logic', [])]
            
            # 암기 카테고리
            M_selection = st.pills("암기 카테고리", M_options, selection_mode="multi")
            if sorted(M_selection) == sorted(M_options):
                ability_M = st.slider("당신의 암기 능력은?", 0, 100, a_for_M)
    
            # 수리 카테고리
            C_selection = st.pills("수리 카테고리", C_options, selection_mode="multi")
            if sorted(C_selection) == sorted(C_options):
                ability_C = st.slider("당신의 수리 능력은?", 0, 100, a_for_C)
    
    
            # 논리 카테고리
            L_selection = st.pills("논리 카테고리", L_options, selection_mode="multi")
            if sorted(L_selection) == sorted(L_options):
                ability_L = st.slider("당신의 논리력은?", 0, 100, a_for_L)
    
            I = [ability_M, ability_C, ability_L]
    
        with st.container(border=True):
            st.markdown("<h3 style='color:#E74C3C;'>시험일까지 D-Day 입력하기</h3>",unsafe_allow_html=True)
            st.markdown("---")
    
            cols, cols_blank = st.columns([8, 2])#입력칸 크기 조절
    
            with cols:
                for sub in combined_list:
                    num = st.number_input(sub, value=None, placeholder="시험일까지 남은 일수를 입력해주세요")
                    x.append(num)
    
    
        with st.container(border=True):
            # 9~0일 전 알바, 수업 시간 받기 버튼
            subjects = list(range(1, 11))  # ← 10개
            st.markdown("<h3 style='color:#E74C3C;'>공부 불가 시간 입력하기</h3>", unsafe_allow_html=True)
            st.text("N일차에 수업이나 알바로 인해 공부가 불가한 시간을 입력해주세요")
            st.markdown("---")
            cols = st.columns(10)  # 열 10개 생성
            work_dict = {}
    
            for subj, col in zip(subjects, cols):
                with col:
                    work_dict[subj] = st.number_input(
                        label=f"{subj}일차",
                        min_value=0,
                        placeholder="시험일까지 남은 일수",
                        step=1,
                        format="%d",
                        key=f"days_{subj}",
                    )
    
            st.markdown("<div style='text-align:center; margin-top:20px;'>", unsafe_allow_html=True)
            run = st.button("🔍 최적의 스케쥴 찾기", use_container_width=True, key='run_btn')#멘트수정
            st.markdown("</div>", unsafe_allow_html=True)


import numpy as np
import gurobipy as gp
from gurobipy import GRB

# --- 2. "실행" 버튼을 눌렀을 때의 로직 ---
if run:
    with st.spinner('🔥 최적의 계획을 계산하는 중입니다... 잠시만 기다려주세요...'):
       # ▼▼▼▼▼ 기존의 모든 Gurobi 모델링 및 최적화 코드를 이 안에 그대로 넣습니다 ▼▼▼▼▼
       # (OLS, 파라미터 계산, 모델 생성, 제약조건 추가, 최적화 실행 등)
       
       # --- 최적화 논리 코드 시작 (수정 없음) ---
       results = st.session_state.results
       subject_value = [int(i) for i in results['credits']] # 과목별 학점 리스트임 과목 정렬 순서 유지됨
       sweetness_subject = [int(j) for j in results['sweetness']] # 과목별 당도 구한거 리스트임
       dict_subject = results['sorted_dict'] # {'memorize' : [], 'math': [], 'logic': [],'unknown': []} 형태
       # --- 최적화 논리 코드 시작 (수정 없음) ---
       sweetness_per = [sweetness_subject[i]/subject_value[i] for i in range(len(subject_value))]
       sweetness_rev = [round(1/sweetness_per[i],4) for i in range(len(sweetness_per))]

       s = len(dict_subject['memorize'])*I[0]+len(dict_subject['math'])*I[1]+len(dict_subject['logic'])*I[2]
       n = [I[0]]*len(dict_subject['memorize'])+[I[1]]*len(dict_subject['math'])+[I[2]]*len(dict_subject['logic'])
       I = [-i/s for i in n]
       
       norma_sweetness = [i / sum(sweetness_rev) for i in sweetness_rev]
       subject_dict = {}
       for i in range(len(x)):
           subject_dict[combined_list[i]] = (int(x[i]), norma_sweetness[i] * 20)

       EV_value = [sweetness_subject[i]*subject_value[i] for i in range(len(subject_value))]

       num = []
       for j in x:
           num_list = []
           for i in range(10):
               value = int(j) - (i + 1)
               if value > 0:
                   num_list.append(value)
               else:
                   num_list.append(0)
           num.append(num_list)

       transposed = list(zip(*num))
       #w값 수정-----------------------
       avg_by_index = [sum(col) / len(col) for col in transposed]
       EV = np.mean(EV_value)
       w_i = [(EV / avg) if avg != 0 else 0 for avg in avg_by_index] #평균 잔여일 작아지면 스트레스 가중치 증가
       
       d = -0.9655
       R_j_pass = -5.5471 / 10.6362;
       R_j_fail = -1.2214 / 10.6362;
       R_j_drop = 3.8677 / 10.6362

       a_j = [np.round((100/(4+0.9655))*i, 3) for i in norma_sweetness]
       b_j = [np.round((100/(4+0.9655))* j, 3) for j in I]
       wi_norm = [np.round((100/(4+0.9655)) * i / sum(w_i), 3) for i in w_i] #wi_value값 w_i로 대체
       #------------------------------

       d = np.round(d *(100/(4+0.9655)), 3)
       R_j_pass = np.round(R_j_pass * (100/(4+0.9655)), 3);
       R_j_fail = np.round(R_j_fail * (100/(4+0.9655)), 3);
       R_j_drop = np.round(R_j_drop *(100/(4+0.9655)), 3)

       m = gp.Model("stress_model")
       I_days = range(10)
       J_tasks = range(len(combined_list))
       a = len(dict_subject['memorize']) ; b = len(dict_subject['memorize'])+len(dict_subject['math']) 
       P_F_std_1 = [17*sweetness_rev[i] for i in range(a)]
       P_F_std_2 = [30*sweetness_rev[i] for i in range(a,b)]
       P_F_std_3 = [25*sweetness_rev[i] for i in range(b,len(sweetness_subject))]
       P_F_std = P_F_std_1 + P_F_std_2 + P_F_std_3
       X_ij = m.addVars(I_days, J_tasks, vtype=GRB.CONTINUOUS, lb=0, ub=8, name="X")
       Y_i = m.addVars(I_days, vtype=GRB.CONTINUOUS, lb=4, name="Y")
       Z_i = m.addVars(I_days, vtype=GRB.CONTINUOUS, lb=0, name="Z")
       r_1j = m.addVars(J_tasks, vtype=GRB.BINARY, name="r_pass")
       r_2j = m.addVars(J_tasks, vtype=GRB.BINARY, name="r_fail")
       r_3j = m.addVars(J_tasks, vtype=GRB.BINARY, name="r_drop")
       S_i = m.addVars(I_days, vtype=GRB.CONTINUOUS, lb=0, name="S")
       R_j = m.addVars(J_tasks, vtype=GRB.CONTINUOUS, lb=-GRB.INFINITY, name="R")

       #수면시간에 대한 스트레스 감소 가중치------------
       T = 24 # 하루는 24시간
       q = [None]*T
       for t in range(T):
           if 0 <= t < 4:
               q[t] = -6.063
           elif 4 <= t < 8:
               q[t] = -5.063
           elif 8 <= t < 16:
               q[t] = -4.063
           elif 16 <= t < 20:
               q[t] = -5.063
           else:  # 20 <= t < 24
               q[t] = -6.063  


       # i번째 날 수면시간
       y_it = m.addVars(I_days, T, vtype=GRB.BINARY, name="sleep")   # t에서 자면 1
       start_it = m.addVars(I_days, T, vtype=GRB.BINARY, name="start")   # t에서 수면 시작
       end_it = m.addVars(I_days, T, vtype=GRB.BINARY, name="end")     # t에서 수면 종료
       
       Y_w = []
       for i in I_days:
           y_wi = gp.quicksum(q[t]*y_it[i,t] for t in range(T))
           Y_w.append(y_wi)

       # 수면 시간 계산 제약
       for i in I_days:
           for t in range(T):
               m.addConstr(y_it[i,t] - y_it[i,(t-1) % T] == start_it[i,t] - end_it[i,t], name=f"flow_{t}")
   
           m.addConstr(gp.quicksum(start_it[i , t] for t in range(T)) == 1, name="one_start")
           m.addConstr(gp.quicksum(end_it[i , t] for t in range(T)) == 1, name="one_end")
       for i in I_days:
           m.addConstr(Y_i[i] == gp.quicksum(y_it[i, t] for t in range(T)), name="Y_def_{i}")
       #-------------------------------------------

       # 공부 시작 여부 변수 추가-------
       h_ij = m.addVars(I_days, J_tasks, vtype=GRB.BINARY, name="h") 

       for i in I_days:
           a_term = gp.quicksum(a_j[j] * X_ij[i, j] for j in J_tasks)
           b_term = gp.quicksum(b_j[j] * h_ij[i, j] for j in J_tasks) #시작시에만 b_j 적용
           m.addConstr(S_i[i] >= a_term + b_term +  Y_i[i] + d * Z_i[i], name=f"S_def_{i}")
       bigM = 1000
       for i in I_days:
           for j in J_tasks:
               m.addConstr(X_ij[i, j] <= bigM * h_ij[i, j], name=f"X_h_link1_{i}_{j}")
               m.addConstr(X_ij[i, j] >= 0.001 * h_ij[i, j], name=f"X_h_link2_{i}_{j}") #공부시간 0이면 h_ij[i, j] = 0
       
       for i in I_days:
           m.addConstr(gp.quicksum(h_ij[i,j] for j in J_tasks) <= 3, name=f"max_subjects_{i}") #하루 최대 세과목 가능(결과에 부작용 있으면 삭제 가능)
       #-----------------------------

       for j in J_tasks:
           m.addConstr(R_j[j] == R_j_pass * r_1j[j] + R_j_fail * r_2j[j] + R_j_drop * r_3j[j], name=f"R_def_{j}")

       for i in I_days:
           m.addConstr(gp.quicksum(X_ij[i, j] for j in J_tasks) + Y_i[i] + Z_i[i] == 19 - work_dict[i + 1],
                       name=f"time_budget_{i}")

       for i in I_days:
           for j in J_tasks:
               subj = combined_list[j]
               if subject_dict[subj][0] <= i + 1:
                   m.addConstr(X_ij[i, j] == 0, name=f"deadline_{i}_{j}")

       avg_S = gp.quicksum(S_i[i] for i in I_days) / len(I_days)
       for i in I_days:
           m.addConstr(S_i[i] <= 5 * avg_S, name=f"stress_limit_{i}")

       m.addConstr(gp.quicksum(X_ij[i, j] for i in I_days for j in J_tasks) >= 38.85, name="min_total_study")

       avg_sleep = gp.quicksum(Y_i[i] for i in I_days) / len(I_days)
       m.addConstr(avg_sleep >= 7.024, name="min_avg_sleep")

       k_i = [sum(1 for subj in combined_list if subject_dict[subj][0] == i + 1) for i in I_days]
       for i in I_days:
           m.addConstr(Z_i[i] >= k_i[i], name=f"min_leisure_{i}")

       for j in J_tasks:
           m.addConstr(r_1j[j] + r_2j[j] + r_3j[j] == 1, name=f"grade_choice_{j}")

       E = 0.0001
       M = 10000
       for j in J_tasks:
           total_Xj = gp.quicksum(X_ij[i, j] for i in I_days)
           m.addConstr(total_Xj >= P_F_std[j] + E - M * (1 - r_1j[j]), name=f"pass_lb_{j}")
           m.addConstr(total_Xj <= M * r_1j[j], name=f"pass_ub_{j}")

       for j in J_tasks:
           total_Xj = gp.quicksum(X_ij[i, j] for i in I_days)
           m.addConstr(total_Xj >= E - M * (1 - r_2j[j]), name=f"fail_lb_{j}")
           m.addConstr(total_Xj <= P_F_std[j] + M * (1 - r_2j[j]), name=f"fail_ub_{j}")

       for j in J_tasks:
           total_Xj = gp.quicksum(X_ij[i, j] for i in I_days)
           m.addConstr(total_Xj <= M * (1 - r_3j[j]), name=f"drop_ub_{j}")
           m.addConstr(total_Xj >= -M * (1 - r_3j[j]), name=f"drop_lb_{j}")

       m.addConstr(gp.quicksum(r_3j[j] for j in J_tasks) <= 2, name="max_one_drop")

       obj = gp.quicksum(wi_norm[i] * S_i[i] for i in I_days) + gp.quicksum(R_j[j] for j in J_tasks) #wi_value값 wi_norm으로 대체
       m.setObjective(obj, GRB.MINIMIZE)

       m.optimize()

       #스트레스정도출력----------
       # 목적함수 값(obj)이 best_obj(예:-40)일 때 100점, worst_obj(예:0)일 때 0점
       best_obj =-6; worst_obj = 4
       stress_score = (worst_obj - m.ObjVal) / (worst_obj - best_obj) * 100
       # 0~100 범위로 제한
       stress_score = max(0, min(100, stress_score))
       print(f"최적화된 스트레스 점수: {stress_score:.2f}점")
       #------------------------

       # --- 최적화 논리 코드 끝 (수정 없음) ---

        # --- 3. 최적화 결과를 session_state에 저장 (핵심!) ---
       if m.status == GRB.OPTIMAL:
            st.session_state.gurobi_results = {
                "status": "OPTIMAL",
                "Obj_val" : m.ObjVal,
                "X_ij": m.getAttr('X', X_ij),
                "Y_i": m.getAttr('X', Y_i),
                "Z_i": m.getAttr('X', Z_i),
                "start_it": m.getAttr('X', start_it), 
                "end_it": m.getAttr('X', end_it),
                "r_1j": m.getAttr('X', r_1j),
                "r_2j": m.getAttr('X', r_2j),
                "r_3j": m.getAttr('X', r_3j),
                "subject": combined_list, "work_dict": work_dict,
                "I_days": I_days, "J_tasks": J_tasks,
                "T": T
            }
       elif m.status == GRB.INFEASIBLE:
            st.session_state.gurobi_results = {"status": "INFEASIBLE"}
       else:
            st.session_state.gurobi_results = {"status": "NOT_OPTIMAL"}

# --- 4. 결과 표시 로직 ---
# 이 부분은 "if run:" 블록 밖에 위치해야 합니다.
# session_state에 결과가 저장되어 있는지 확인하고, 있다면 화면에 표시합니다.
with schedule_tab:
    if st.session_state.gurobi_results:
        results = st.session_state.gurobi_results

        st.markdown(
            "<div style='text-align:center; font-size:28px; font-weight:700; margin-top:12px;'> 가젤이 치타를 잡아먹는 법 </div>",
            unsafe_allow_html=True
        )
        st.divider()

        if results["status"] == "INFEASIBLE":
            st.error("모델이 infeasible합니다. 제약 조건을 확인하세요.")
        elif results["status"] == "NOT_OPTIMAL":
            st.warning("최적해를 찾지 못했습니다. 모델 상태를 확인하세요.")
        elif results["status"] == "OPTIMAL":
            st.header("🔍 일자별 학습 계획 조회")

            # 여기서 Day 값을 바꿔도 Gurobi는 다시 실행되지 않습니다.
            input_day = st.number_input(
                label="Day :", min_value=1, max_value=len(results["I_days"]),
                step=1, help=f"1부터 {len(results['I_days'])} 사이의 숫자를 입력하세요."
            )
            st.subheader(f"✅ Day {input_day} 최적 시간 배분 결과")

            day_index = input_day - 1
            total_study = sum(results["X_ij"][day_index, j] for j in results["J_tasks"])

            잔여시간 = 19 - results["work_dict"][input_day]
            with st.container(border=True):
               # 최적 스트레스 점수 출력
               st.write("**최적 스트레스 및 수면 계획**")
               st.metric(label="계산된 스트레스 총합", value=f"{results['Obj_val']:.2f}", help="이 값이 낮을수록 최적의 계획입니다.")
               
               # 선택된 날짜의 수면/기상 시간 찾기
               start_time = -1
               end_time = -1
               for t in range(results["T"]):
                   if results["start_it"][day_index, t] > 0.5:
                       start_time = t
                   if results["end_it"][day_index, t] > 0.5:
                       end_time = t
               
               st.markdown(f"&nbsp;&nbsp;&nbsp;- 수면 시작: **`{start_time:02d}:00`**")
               st.markdown(f"&nbsp;&nbsp;&nbsp;- 기상 시간: **`{end_time:02d}:00`**")
            
            with st.container(border=True):
                st.write("**상세 공부 계획**")
                for j in results["J_tasks"]:
                    x_val = results["X_ij"][day_index, j]
                    if x_val > 0.01:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;- {results['subject'][j]} 공부: `{x_val:.2f}`시간")
                st.markdown(f"&nbsp;&nbsp;&nbsp;- 수면: `{results['Y_i'][day_index]:.2f}`시간")
                st.markdown(f"&nbsp;&nbsp;&nbsp;- 여가: `{results['Z_i'][day_index]:.2f}`시간")
            with st.container(border=True):
                sleep_schedule = []
                # 10일 동안 반복
                for i in results['I_days']:
                    start_time = -1
                    end_time = -1
                    
                    # 24시간 동안 반복하며 수면 시작/종료 시간 찾기
                    for t in range(results['T']):
                        # start_it[i, t] 변수의 최적값이 1에 가까우면 해당 시간이 시작 시간임
                        if results['start_it'][i, t] > 0.5:
                            start_time = t
                        # end_it[i, t] 변수의 최적값이 1에 가까우면 해당 시간이 종료 시간임
                        if results['end_it'][i, t] > 0.5:
                            end_time = t
                
                # 찾은 시간을 딕셔너리 형태로 저장
                schedule_data = {
                    "날짜": f"{i+1}일차",
                    "수면 시간": f"{start_time:02d}:00",
                    "기상 시간": f"{end_time:02d}:00"
                }
                sleep_schedule.append(schedule_data)

            # st.dataframe을 사용해 표 형태로 깔끔하게 출력
            st.dataframe(sleep_schedule, use_container_width=True)
                

            with st.expander("과목별 최종 성적 결과 보기"):
                st.markdown("---")
                for j in results["J_tasks"]:
                    subj_name = results["subject"][j]
                    if results["r_1j"][j] > 0.5:
                        result = "PASS"
                    elif results["r_2j"][j] > 0.5:
                        result = "FAIL"
                    elif results["r_3j"][j] > 0.5:
                        result = "DROP"
                    else:
                        result = "UNKNOWN"
                    st.markdown(f"&nbsp;&nbsp;&nbsp;- **{subj_name}**: {result}")
    else:
        # 아직 실행 버튼을 누르지 않은 초기 화면
        st.markdown(
            "<div style='text-align:center; font-size:24px; font-weight:500; margin-top:12px;'>🔥 버튼을 눌러 시작하세요! 🔥</div>",
            unsafe_allow_html=True
        )






#=======타이머 로직(변경할 필요 x)=======
# 오른쪽: 타이머
with timer_tab:
    with st.container(border=True):
        st.markdown("<h3 style='color:#E74C3C;'>집중력 부스터 타이머 </h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        if "total_sec" not in st.session_state:
            st.session_state.total_sec = 15 * 60   # 기본 15분
        if "start_ts" not in st.session_state:
            st.session_state.start_ts = None
        if "running" not in st.session_state:
            st.session_state.running = False
        if "show_start_msg" not in st.session_state:
            st.session_state.show_start_msg = False
        if "finished_once" not in st.session_state:
            st.session_state.finished_once = False

        def fmt_mmss(sec: int) -> str:
            m, s = divmod(max(0, int(sec)), 60)
            return f"{m:02d}:{s:02d}"

        def remaining_sec() -> int:
            if st.session_state.running and st.session_state.start_ts:
                elapsed = time.time() - st.session_state.start_ts
                return max(0, int(st.session_state.total_sec - elapsed))
            return int(st.session_state.total_sec)

        def set_preset_minutes(mins: int):
            """좌측 프리셋/직접입력: 시간 '설정만' (시작은 우측 버튼으로)"""
            st.session_state.total_sec = int(mins * 60)
            st.session_state.start_ts = None
            st.session_state.running = False
            st.session_state.finished_once = False

        def start_timer():
            if not st.session_state.running:
                # 설정된 남은시간 기준으로 시작
                secs = remaining_sec()
                st.session_state.total_sec = secs if secs > 0 else st.session_state.total_sec
                st.session_state.start_ts = time.time()
                st.session_state.running = True
                st.session_state.finished_once = False
                st.session_state.show_start_msg = True

        def pause_timer():
            if st.session_state.running:
                st.session_state.total_sec = remaining_sec()
                st.session_state.running = False
                st.session_state.start_ts = None

        def reset_timer():
            st.session_state.running = False
            st.session_state.start_ts = None
            st.session_state.finished_once = False

        # 레이아웃 (구조 최대한 유지)
        left, right = st.columns([10, 12])

        with left:
            st.text("빠른 타이머")
            # 타이머 버튼들 (이제는 '설정'만)
            tcol1, tcol2, tcol3,r = st.columns([4, 4, 4,0.5])
            with tcol1:
                if st.button("1분 타이머",):
                    set_preset_minutes(1)
            with tcol2:
                if st.button("2분 타이머"):
                    set_preset_minutes(2)
            with tcol3:
                if st.button("5분 타이머"):
                    set_preset_minutes(5)

            duration_input = st.number_input("직접 설정 (분)", min_value=1, max_value=180,
                                            value=max(1, remaining_sec() // 60), step=1)
            
            if st.button("시간 설정", use_container_width=True):    
                set_preset_minutes(int(duration_input))

        with right:
            # 상단 컨트롤(시작/일시정지/리셋)
            b1, b2, b3 = st.columns(3)
            with b1:
                st.button("▶ 시작", use_container_width=True, on_click=start_timer,
                        disabled=st.session_state.running)
            with b2:
                st.button("⏸ 일시정지", use_container_width=True, on_click=pause_timer,
                        disabled=not st.session_state.running)
            with b3:
                st.button("↺ 리셋", use_container_width=True, on_click=reset_timer)


            # 진행 영역
            secs = remaining_sec()
            st.markdown(f"### ⏱ {fmt_mmss(secs)} 남음")

            # 진행률 바(경과/총)
            if st.session_state.running and st.session_state.start_ts:
                elapsed = st.session_state.total_sec - secs
                progress_ratio = min(1.0, max(0.0, elapsed / max(1, st.session_state.total_sec)))
            else:
                progress_ratio = 1 - (secs / max(1, st.session_state.total_sec))
            st.progress(progress_ratio)


            # 종료 처리
            if st.session_state.running and secs <= 0:
                # 여기서는 rerun 하지 않음 → 바로 연출이 보임
                st.session_state.running = False
                st.session_state.start_ts = None
                if not st.session_state.finished_once:
                    st.session_state.finished_once = True
                    st.balloons()
                    st.success("⏰ 집중 끝! 고생했어요.")
                    # 팁 유지
                    st.info("💡 팁: 25분 집중 + 5분 휴식(뽀모도로)을 반복해 보세요.")
                    # 랜덤 응원 메시지 (네 스타일 그대로)
                    messages = [
                        "노력은 배신하지 않는다.",
                        "오늘 걷지 않으면 내일은 뛰어야 한다.",
                        "시간이 부족하다는 건 핑계일 뿐!",
                        "10시간이 부족하다면 10배로 집중해라.",
                        "아무것도 하지 않으면 아무 일도 일어나지 않는다."
                    ]
                    msg = random.choice(messages)
                    st.markdown(f"""
                    <div style="border: 2px dashed #FF6B6B; padding: 12px; border-radius: 10px; background-color: #ffffff;">
                        <h4 style="color: #FF6B6B;"> 오늘의 응원 멘트</h4>
                        <p style="text-align:center;">{msg}</p>
                    </div>
                    """, unsafe_allow_html=True)

        # 틱 업데이트 (부드러운 갱신)
        if st.session_state.running and remaining_sec() > 0:
            time.sleep(0.1)
            st.rerun()