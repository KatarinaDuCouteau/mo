import React from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types';
import { Table, Icon } from 'antd';

import style from './table.css';

const getColumns = (props) => {
  let line = props.data.table[0];
  let Columns = Object.keys(line).map((e) =>
    {
      if(props.data.X_fields.indexOf(e) !== -1){
        if(props.data.labels[props.data.X_fields.indexOf(e)]) {
          return({
            title : e,
            dataIndex: e,
            key: e,
            width: 100,
            fixed: 'right',
            className: style.fields,
            render: text =>
              <div>
                <span style={{color: 'rgba(192, 149, 122, 1)'}}>{text}</span>
              </div>
          })
        }else{
          return({
            title : e,
            dataIndex: e,
            key: e,
            width: 100,
            fixed: 'right',
            className: style.fields,
            render: text =>
              <div>
                <span>{text}</span>
              </div>
          })
        }

      }else if(props.data.Y_target.indexOf(e) !== -1){
        return({
          title : e,
          dataIndex: e,
          key: e,
          width: 100,
          fixed: 'right',
          className: style.target,
          render: text =>
            <div>
              <span>
                {text}
              </span>
            </div>
        })
      }else{
        return({
          'title' : e,
          'dataIndex': e,
          'key': e,
          'width': 100,
          'fixed': 'right'
        })
      }
    }
  )
  return Columns
}

const getData = (props) => {
  let data  = props.data.table;
  return [data[0], data[1], data[2], data[3]]
}

export default (props) => {
  //console.log(props);
  return <Table size='small'
                scroll={{ x: 800 }}
                rowKey={record => record._id}
                columns={getColumns(props)}
                dataSource={getData(props)}
                pagination={false}
                />
}