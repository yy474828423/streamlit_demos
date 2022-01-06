import streamlit as st
import pandas as pd
import re


P = re.compile(",|，|\\s+")

class T:
    def __init__(self,file_dir):
        self.t = self.read_table(file_dir)
    
    @staticmethod
    def read_table(file_dir):
        '''读取标准模型表'''
        f = open(file_dir,'r')
        a = f.read()
        dict_name = eval(a)
        f.close()
        return dict_name 

    def show_tables(self,tbs):
        '''展示表内容'''
        def show_detal(k1,k2):
            '''获取输入表的字段信息'''
            en,cn,insr=[],[],[]
            for v in self.t[k1][k2]:
                en.append(v[0])
                cn.append(v[1])
                insr.append(v[4])
            df = pd.DataFrame({'EN':en,'CN':cn,'INSR':insr})
            return df

        def find_table(tb):
            '''搜寻目标表，并获取其字段'''
            for k in self.t:
                for k_ in self.t[k].keys():
                    tb_name = str.split(k_,' ')[0]
                    if tb_name == tb:
                        ans = show_detal(k,k_)
                        return k,k_,ans

        final_res = []
        for tb in tbs:
            if tb:
                final_res.append(find_table(tb.strip()))
        return final_res
   
    def search_fields(self,info,lang='cn',layer=None,fuzzy=False):
        """
        输入字段与全部字段进行匹配
        info: 输入可以是字符串，也可以是列表（多个字段）
        lang: 搜索字段 ，英文字段名：'en'，
                        字段中文名： 'cn'，
                        字段说明：'instruction'（字段说明搜索仅适用于单字段、模糊搜索）
        layer: 模型表数仓层，需大写，如'DM','DW'
        fuzzy: 是否模糊匹配，适用于单字段模糊匹配
        """
        idx = 1
        if lang == 'en':
            idx = 0
        elif lang=='cn':
            idx = 1
        elif lang=='instruction':
            idx = 4
            fuzzy=True

        ans = []
        for k1 in self.t:
            if not layer or (layer and layer in k1): 
                for k2,v in self.t[k1].items():
                    inner = []
                    for val in v:
                        if len(info) == 1:
                            _info = info[0]
                            if fuzzy:
                                if _info in val[idx]:
                                    inner.append((val[0],val[1],val[4]))
                            else:
                                if val[idx] == _info:
                                    inner.append((val[0],val[1],val[4]))
                        else:
                            if val[idx] in info:
                                inner.append((val[0],val[1],val[4]))
                    inner_len = len(inner)
                    if inner:
                        ans.append((k1,k2,inner_len,inner))

        if ans:
            tbs_sort = sorted(ans,key=lambda x:x[2],reverse=True)
            return tbs_sort        


class st_elements:
    def __init__(self) -> None:
        col1,col2= st.columns([1,3])
        with col1:
            st.image('https://www.hundsun.com/assets/img/logo.18ce4e5c.png')
        with col2:
            st.title('模型搜索小工具')
        self.create_block()
    
    @staticmethod
    def my_radio(name,option,key,help=None):
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>', unsafe_allow_html=True)
        st.write('<style>div.st-bf{flex-direction:row;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)
        ans = st.radio(name,option,key=key,help=help)
        return ans

    def field_search(self,key):
        '''模型字段搜索控件组合'''
        st.subheader('窗口 '+str(key)+'&emsp; ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~')
        col1,col2,col3= st.columns([2,1,1])
        with col1:
            language=self.my_radio("查询字段",("字段中文","字段中文","字段说明"),key=key)
        with col2:
            st.write('---')
            fuzzy = st.checkbox('模糊搜索',help='模糊搜索只适用于单个字段，多字段搜索无效',key=key)
        with col3:
            st.write('---')
            expand = st.checkbox('全表数据展示',help='可展开展示全表字段，但影响生成速度',key=key)  
        lay = st.selectbox('需要查询哪层数据?',('DW', 'DM', 'DIM', 'ODS','数据字典','All'),key=key,help='查询模型分层，ODS&数据字典暂不支持')
        key_words = st.text_input('请输入你想查询的信息:', '',help='字段信息，支持多字段，多字段请用单个中英文逗号或空格隔开，请勿多加空格',key=key)
        if key_words:
            lay = None if lay=='All' else lay
            words = P.split(key_words)
            la = {'字段英文':'en','字段中文':'cn','字段说明':'instruction'}[language]
            result = tb.search_fields(info=words,lang=la,layer=lay,fuzzy=fuzzy)
            if result:
                for _ in result:
                    st.markdown(f'**{_[1]}**&emsp;&emsp;{_[0]}&emsp;&emsp;【{_[2]}】')
                    for _val in _[3]:
                        st.markdown(f'**EN: **`{_val[0]}`&emsp;&emsp;**CN: **`{_val[1]}`&emsp;&emsp;**INSR: **`{_val[2]}`')
                    # st.dataframe(pd.DataFrame({'EN':[_[2]],'CN':[_[3]],'INSR':[_[4]],}))
                    if expand:
                        with st.expander("view more"):
                            table_name = _[1].split(' ')[0]
                            tables = tb.show_tables([table_name])
                            if tables:
                                for table in tables:
                                    st.write(table[2])
                    else:
                        st.markdown('---')
            else:
                st.markdown('no table has such field in layer {}'.format(lay))
    
    def modle_search(self,key):
        '''模型表搜索控件组合'''
        st.subheader('窗口 '+str(key)+'&emsp; ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~')
        table_name = st.text_input('请输入你想查询的模型:', '',help='按英文表名搜索，多张表请用单个中英文逗号或空格隔开，支持多个空格',key=key)
        if table_name:
            table_in = P.split(table_name)
            tables = tb.show_tables(table_in)
            if tables:
                for table in tables:
                    st.markdown(f'**{table[1]}**&emsp;&emsp;{table[0]}')
                    st.write(table[2])
            else:
                st.write('no such table')

    def block_head(self,head,name,option,key,help=None):
        """组件块头部:标题与查询窗口数"""
        col1,col2= st.columns([2,3])
        with col1:
            st.header(head)
        with col2:
            return self.my_radio(name,option,key=key,help=help)
    
    def create_block(self):
        """创建组件块"""
        field_search_num = self.block_head('字段搜索',"查询窗口个数",("1","2","3",'4','5'),'fields_origin')
        for i in range(int(field_search_num)):
            self.field_search(key=i+1)
        modle_search_num = self.block_head('模型搜索',"查询窗口个数",("1","2","3"),'modles_origin')
        for i in range(int(modle_search_num)):
            self.modle_search(key=i+1)
        etl_search_num = self.block_head('ETL脚本搜索',"查询窗口个数",("1","2","3",'4','5'),'ETL_origin',help='待完善')
        for i in range(int(etl_search_num)):
            st.text_input('请输入你想查询的模型:', '待完善',help='待完善',key='10086')
        ind_search_num = self.block_head('指标搜索',"查询窗口个数",("1","2","3",'4','5'),'IND_origin',help='待完善')
        for i in range(int(ind_search_num)):
            st.text_input('请输入你想查询的模型:', '待完善',help='待完善',key='10001')
        

if __name__ == '__main__':
    # streamlit run f:/pycode/模型表数据读写/streamlit_server.py
    # 'F:\pycode\模型表数据读写\data\models_dict.txt'
    main_1 = st.text_input('请输入文件地址:', '',help='模型导出excel地址',key='main_1')
    if main_1:
        tb = T(main_1)
        my_st = st_elements()
