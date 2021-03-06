import React from 'react'
import {
  LocaleProvider, Pagination, DatePicker, TimePicker, Calendar,
  Popconfirm, Table, Modal, Button, Select, Transfer, Radio, Layout
} from 'antd'
import {  } from 'antd';
const { Footer, Sider, Content } = Layout;
import {IntlProvider} from 'react-intl'
import enUS from 'antd/lib/locale-provider/en_US'
import {WebChat} from "../Chat"
import {WorldChannel, Open} from '../WorldChannel'

// ant design 组件国际化包
import moment from 'moment'
import 'moment/locale/zh-cn'

moment.locale('en')

import styles from './MainLayout.less'
import Header from './Header'

import zh_CN from '../../intl/zh_CN'
import en_US from '../../intl/en_US'

function MainLayout({children, location, history, modal, isRight, onClickIcon}) {
  return (
    <Layout style={{height: '100%'}}>
      <Header location={location} history={history} />
      <Content style={{display: "flex"}}>
        <div className={styles.content}>
          {children}
        </div>
        <Open onClickIcon={onClickIcon} isRight={isRight}/>
      </Content>
    </Layout>
  )

  return (
    <div className={styles.container}>
      <div>
        <Header location={location} history={history}/>
      </div>
      {/*<div style={{display: "flex", flex:1,  width: "100%"}}>*/}
        <div className={styles.content}>
          {children}
        </div>
        {/*<Open onClickIcon={onClickIcon} isRight={isRight}/>*/}
      {/*</div>*/}
      {/*<Button type="primary" onClick={modal.showModal}>Open</Button>*/}

      {/*<Modal*/}
      {/*title="Basic Modal"*/}
      {/*visible={modal.visible}*/}
      {/*onOk={modal.handleOk}*/}
      {/*onCancel={modal.handleCancel}*/}
      {/*>*/}
      {/*<WorldChannel/>*/}
      {/*</Modal>*/}


    </div>
  )
}


class OutMainLayout extends React.Component {
  constructor() {
    super()
    this.state = {
      locale: enUS,
      language: en_US,

      worldChannelIsOpen: false,
      visible: true,

      isRight: false
    }
  }

  // state = { visible: true }

  showModal = () => {
    this.setState({
      visible: true,
    })
  }
  handleOk = (e) => {
    console.log(e)
    this.setState({
      visible: false,
    })
  }
  handleCancel = (e) => {
    console.log(e)
    this.setState({
      visible: false,
    })
  }

  changeLocale = (e) => {
    const localeValue = e.target.value
    this.setState({locale: localeValue})
    if (!localeValue) {
      moment.locale('zh-cn')
      this.setState({
        language: zh_CN
      })

    } else {
      moment.locale('en')
      this.setState({
        language: en_US
      })
    }
  }

  render() {
    return (
      <div style={{height: '100%'}}>
        {/*<div className="change-locale">*/}
        {/*<span style={{marginRight: 16}}>Change locale of components: </span>*/}
        {/*<Radio.Group defaultValue={enUS} onChange={this.changeLocale}>*/}
        {/*<Radio.Button key="en" value={enUS}>English</Radio.Button>*/}
        {/*<Radio.Button key="cn">中文</Radio.Button>*/}
        {/*</Radio.Group>*/}
        {/*</div>*/}

        <LocaleProvider locale={this.state.locale}>
          <IntlProvider
            locale={'en'}
            messages={this.state.language}
          >
            <MainLayout
              location={this.props.location}
              history={this.props.history}
              children={this.props.children}
              modal={{
                visible: this.state.visible,
                showModal: this.showModal,
                handleOk: this.handleOk,
                handleCancel: this.handleCancel
              }}
              isRight={this.state.isRight}
              onClickIcon={() => this.setState({isRight: !this.state.isRight})}
            />

          </IntlProvider>

        </LocaleProvider>

        <WebChat isRight={this.state.isRight}/>
      </div>
    )
  }
}


export default OutMainLayout
