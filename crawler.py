import traceback
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import openai
import streamlit as st
import time
import json

openai_key = st.secrets["openai_key"]
client = openai.OpenAI(api_key = openai_key)

def review_adjust(x):
    if isinstance(x, str):
            x = x.replace('천','')
            x = x.strip()
            x = float(x) * 1000
            return x
    else:
        return x

def rating_adjust(x):
    try:
        return float(x)
    except:
        return 0



def text_summary(text):
    assistant_id = 'asst_VXt1MgwX1BWqa4eN1zu7Qrlp'
    thread_id = 'thread_aFsEKV8N2wLjGL1qQzA3DMEz'

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role='user',
        content=""" %s \n\n\n
        이 데이터는 구글에서 크롤링해온 맛집 데이터야, 데이터를 {식당목록 : [{식당이름 : 호반, 종류 : 한식, 평점 : 4.3, 리뷰수 : 455, 주소 : 삼일대로 26길 20}, {식당이름 : 청진옥, 종류 : 없음, 평점 : 3.9, 리뷰수 : 3600, 주소 : 삼일대로 26길 20}]} 
        이런식으로 정리를 해줬으면 좋겠어, 참고로 인코딩 혹은 디코딩 오류가 발생할것같은 문장이나 단어는 내용에서 뺴줬으면 좋겠고, , 그리고 메인 키는 '식당목록' 이라고 해줘 """ % text
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    run_id = run.id

    queued_cnt = 0
    while True:
        result = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

        status = result.status
        print(f'Status >> {status}')
        if status == "completed":
            break
        elif status == "in_progress":
            time.sleep(2)
        elif status == "queued":
            queued_cnt += 1
            time.sleep(2)
            if queued_cnt == 10:
                return

        else:
            break

    thread_msg = client.beta.threads.messages.list(thread_id)
    result_value = thread_msg.data[0].content[0].text.value

    try:
        result = json.loads(result_value)
        return result

    except Exception as e:
        error = traceback.format_exc()
        print(error)
        print(result_value)
        return

def execute():
    st.session_state["total_restaurant_df"] = None

    driver = webdriver.Chrome()
    url = 'https://www.google.com'
    driver.get(url)

    search_box = driver.find_element(by = By.CLASS_NAME, value = 'gLFyf')

    search_box.clear()
    search_term = st.session_state["main_state_select"] + ' ' + st.session_state["sub_state_select"] + ' ' + '맛집'
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.ENTER)

    try:
        driver.find_element(by = By.XPATH, value = '//*[@id="Odp5De"]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[2]/div/h3/g-more-link/a/div/span[2]').click()
    except:
        cnt = 1
        while True:
            try:
                driver.find_element(by = By.XPATH, value = f'//*[@id="rso"]/div[{cnt}]/div/div/div[1]/div[5]/div/h3/div/a/div/span[1]').click()
                break
            except:
                print(f'{cnt} 안됨')
                cnt += 1
                continue

        print(f'{cnt}번에서 완료')

    total_text = []

    with st.spinner('맛집 데이터를 수집중입니다 ...'):
        cnt = 0
        while True:
            # cnt += 1
            # if cnt == 4:
            #     break
            try:
                search_result = driver.find_element(by=By.XPATH, value='//*[@id="center_col"]')
                text = search_result.text
                total_text.append(text)
                driver.find_element(by=By.XPATH, value='//*[@id="pnnext"]/span[2]').click()
                time.sleep(2)
            except Exception as e:
                error = traceback.format_exc()
                print(error)
                break

    st.session_state["total_text"] = total_text.copy()
    driver.close()

    total_summary = []
    cnt = 0
    with st.spinner('맛집 데이터를 요약중입니다 ...'):
        for text in st.session_state["total_text"]:
            cnt += 1
            # if cnt == 4:
            #     break
            time.sleep(5)
            print("""===== text 요약을 시작합니다 =====""")
            summary = text_summary(text)
            print("")
            if summary:
                 total_summary.append(summary)
                 print(summary)
                 print("===== 요약 완료 =====")
            else:
                print(f'{cnt} 번 텍스트 에러발생')
                continue


    st.session_state["total_summary"] = total_summary.copy()

    total_df = []
    for summary in st.session_state["total_summary"]:
        try:
            df = pd.DataFrame(summary['식당목록'])
            total_df.append(df)
        except:
            continue

    total_df = pd.concat(total_df)
    total_df.reset_index(drop = True, inplace = True)
    # total_df["평점"] = total_df["평점"].apply(lambda x : rating_adjust(x))
    # total_df["리뷰수"] = total_df["리뷰수"].apply(lambda x : review_adjust(x))

    st.session_state["total_restaurant_df"] = total_df

if __name__ == "__main__":
    execute()