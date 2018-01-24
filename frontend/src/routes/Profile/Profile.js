import React from 'react'
import {connect} from 'dva'
// import styles from './index.less'
import {Tabs, Switch, Button, Input, Form, Card, Icon, Avatar} from 'antd'

import AddModuleModal from "../../components/AddModuleModal"
const {Meta} = Card


function Profile({login, module, dispatch}) {
  const {showModal} = module

  if (login.user) {
    const {age, email, name, phone} = login.user
    return (
      <div style={{display: "flex", flexDirection: "row"}}>
        <Card title={name} extra={<a href="#">Edit</a>} style={{width: 300}}>
          <p>{email}</p>
          <p>{age}</p>
          <p>{phone}</p>
        </Card>

        <Card title={"add module"}  style={{width: 300}}
              onClick={()=>dispatch({
                type: 'module/updateState',
                payload: {
                  showModal: true
                }
              })}
        >
          <p>add module for developer</p>
        </Card>

        <Card title={"add service"}  style={{width: 300}}>
          <p>add service for user</p>
        </Card>

        <AddModuleModal dispatch={dispatch} visible={showModal} />
      </div>
    )
  }
  else {
    return <div/>
  }

}

export default connect(({login, module}) => ({login, module}))(Profile)
