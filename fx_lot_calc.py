import streamlit as st
import yfinance

def check_password():
    """ パスワードが正しいかチェックして、正しければTrueを返す
    """
    def password_entered():
        # 入力されたパスワードが secrets.toml の値と一致するか確認
        if st.session_state['password'] == st.secrets['my_password']:
            # パスワードが正しい場合
            st.session_state['password_correct'] = True
            del st.session_state['password']  # セッションからパスワードを消して安全に
        else:
            # パスワードが誤っている場合
            st.session_state['password_correct'] = False

    if 'password_correct' not in st.session_state:
        # 初回表示
        st.text_input(u'パスワード', type='password', on_change=password_entered, key='password')
        return False

    elif not st.session_state['password_correct']:
        # パスワードが誤っている場合
        st.text_input(u'パスワード', type='password', on_change=password_entered, key='password')
        st.error(u'アクセス拒否')
        return False

    else:
        # パスワードが正しい場合
        return True

def get_fx_rate(pair):
    try:
        sel = '{}=X'.format(pair)
        ticker = yfinance.Ticker(sel)
        fx_rate = ticker.history(period='1d')
        if not fx_rate.empty:
            return fx_rate['Close'].values[-1]
        else:
            return 0.0

    except Exception:
        return 0.0

def calc_lot(target_pair, account_size, risk, pips):
    """
        ・MT4に表示されているpips数は0.1pips計算になっている
        ・250pipsの場合は、MT4上で2500pipsと表示されるので注意
        ・TitanFXは最小ロットが0.01なので注意（0.025ロットとかは取引不可）
    """
    # amount / lot
    lot_base = 100000
    risk = risk/100

    if 'JPY' in target_pair:
        pips_base = 0.01
        lot = (account_size * risk) / (pips * pips_base) / lot_base
    else:
        pips_base = 0.0001
        jpy = get_fx_rate('{}jpy'.format(target_pair[3:]).upper())
        lot = (account_size * risk) / (pips * pips_base) / lot_base / jpy

    #print(u'ロット数 :', lot)
    return lot

def ui():
    st.title(u'FXロット計算')
    cur_pair = ['AUDCAD', 'AUDJPY', 'AUDNZD', 'AUDUSD',
                'CADCHF', 'CADJPY', 'CHFJPY', 'EURAUD',
                'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY',
                'EURNZD', 'EURZAR', 'GBPAUD', 'GBPCAD',
                'GBPCHF', 'GBPJPY', 'GBPNZD', 'GBPUSD',
                'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF',
                'USDJPY', 'USDZAR']

    # ---------------------------------------------------
    # 口座情報・通貨ペア
    st.markdown('### :bank: 口座残高・通貨ペア')

    # 口座残高
    bank = st.number_input(u'口座残高 (円)', value=100000,
                           min_value=0, max_value=10000000)

    # 通貨ペア選択
    cur_pair_index = 0
    sel_pair = st.selectbox(u'通貨ペア', cur_pair, cur_pair_index)

    price = get_fx_rate(sel_pair)
    st.info('1 {} = {:.3f} {}'.format(sel_pair[:3], price, sel_pair[3:]))

    # ---------------------------------------------------
    # リスク
    st.markdown('### :money_with_wings: リスク')

    # 口座残高に対するリスク許容度(%)
    risk = st.number_input(u'リスク許容度 (口座残高に対して何%のリスクを取るか)', value=10,
                           min_value=1, max_value=100)

    # 損切りpips数
    risk_pips = st.number_input(u'損切りpips数', value=20, min_value=0)

    st.markdown('### :currency_exchange: ロット数')

    # ---------------------------------------------------
    # ロット計算
    lot = calc_lot(sel_pair, bank, risk, risk_pips)
    st.info('{:.3f} Lot'.format(lot))

if check_password():
    ui()