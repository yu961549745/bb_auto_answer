""" 自动答题
"""
# %%
import pandas as pd
from fuzzywuzzy import fuzz
from selenium import webdriver

# %% 加载答案
answers = pd.read_excel('整理后答案.xlsx', dtype=str)
# 傻逼 Excel , 这么多乱七八糟的字符
ans_map = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'Ｂ': 2, 'Ｃ': 3,
    '√': '对', 'x': '错', 'X': '错', 'ｘ': '错', '×': '错'
}
# %% 启动和登录
# 答题链接
url = 'https://ks.wjx.top/jq/45065890.aspx'
# url = 'https://ks.wjx.top/jq/45065834.aspx'

# 启动
options = webdriver.ChromeOptions()
driver = webdriver.Chrome('./chromedriver', options=options)
driver.get(url)
# 姓名
driver.find_element_by_id("q1").send_keys('刘彬')
# 公司, 默认选最后一个
driver.find_element_by_css_selector('a[rel="q2_23"]').click()
# 登录
driver.find_element_by_id("btnNext").click()
# 其实所有题目都在页面上了, 但是只显示了一部分
qs = driver.find_elements_by_class_name('div_question')
# %% 自动答题


def get_single_ans(q, answers):
    """ 返回的是答案列表 """
    ratio = answers['题干'].apply(lambda s: fuzz.ratio(s, q))
    res = answers.loc[ratio.idxmax(), :]
    ans = res['试题答案']
    ss = '_ABCD'
    a_list = []
    for a in ans:
        k = ans_map[a]
        if isinstance(k, str):
            a_list.append(k)
        else:
            tmp = res['备选项' + ss[k]]
            if pd.isna(tmp):
                # 选择题有答案没选项的情况
                a_list.append(k)
            else:
                a_list.append(tmp)
    return a_list


# %%
# 根据选项值搜索, 而不是直接填答案
for k in range(2, len(qs)):
    div = qs[k]
    if not div.is_displayed():
        driver.find_element_by_id('btnNext').click()
        print('下一页...')
    q = div.find_element_by_class_name(
        'div_title_question').text
    q = q.split('\n')[0]
    ss = [t.text for t in div.find_elements_by_css_selector('label')]
    ans = get_single_ans(q, answers)
    print(q)
    print(ans)
    ss = pd.Series(ss)
    for a in ans:
        if isinstance(a, str):
            i = ss.apply(lambda s: fuzz.ratio(s, a)).idxmax()
        else:
            i = a - 1
            print('WARNING: 有选项没答案, 原选项为 %s , 实际选项为 %s.' %
                  ('ABCD'[i], ss.iloc[i]))
        div.find_element_by_css_selector(
            'a[rel=q%d_%d]' % (k + 1, i + 1)).click()
# %% 提交
driver.find_element_by_id('submit_button').click()


# %%
