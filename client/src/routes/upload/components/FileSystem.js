import React from 'react'
import { Card, Button, Tabs } from 'antd'
import { connect } from 'dva';
import PropTypes from 'prop-types'
import classnames from 'classnames'

import FileModal from './FileModal'
import { showTime } from '../../../utils/time';
import { jupyterServer, flaskServer } from '../../../constants'
import ImportPanel from './ImportPanel'
import styles from './FileSystem.css'

const TabPane = Tabs.TabPane;

class FileSystem extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      files: [],
    }
  }

  fetchData () {
    fetch(jupyterServer, {
      method: 'get',
    }).then((response) => response.json())
      .then((res) => {
        // console.log(res.content[0].name);
        this.setState({
          files: res.content,
        })
      })
  }

  toggleButton(i) {
    this.props.dispatch({ type: 'upload/toggleButton', payload: i })
  }

  showImportPanel(file) {
    this.props.dispatch({ type: 'upload/showImportPanel', payload: file })
  }

  onClickCard (e, name) {
    e.stopPropagation();
    console.log(name)
    // this.props.toDetail(name)
  }

  onClickDelete(e, _id) {
    // localhost:5000/data/remove_data_set_by_id?data_set_id=59422819df86b2285d9e2cc6
    fetch(flaskServer + '/data/data_sets/' + _id, {
      method: 'delete'
    }).then((response) =>
    {
      if(response.status === 200){
        this.props.dispatch({ type: 'upload/fetch' });
      }
    });
  }

  renderCards (key) {
    let dataSets = this.props.upload.dataSets[key];
    let button = this.props.upload.button;
    //filelist.reverse();
    return dataSets.map((e, i) =>
      <Card key={e._id} title={e.name}
            extra={
              <Button type="danger" style={{marginTop: -5}} onClick={(event) => this.onClickDelete(event, e._id)}>
                DELETE
              </Button>
            }
            style={{ width: 500 }}
            onClick={(ev) => this.onClickCard(ev, e.name)}
            // onMouseOver={() => this.toggleButton(i)}
            // onMouseLeave={() => this.toggleButton(-1)}
      >
        <div className={classnames(styles.flexRow)}>
          <div style={{width: 400}}>
            <p>Description: {e.description}</p>
            {e.file_obj && <p>Upload Time: {showTime(e.file_obj.upload_time)}</p>}
          </div>
          {/*<Button type="primary" style={{ display: button === i ? 'inline':'none' }}*/}
          {/*onClick={() => this.showImportPanel(e)}*/}
          {/*>Import</Button>*/}
        </div>
      </Card>
    );
  }

  renderTabContent(key) {
    const dataSet = this.props.upload.dataSets
    return <div className={classnames(styles.flexRow, styles.fullWidth)}>
      <div style={{ width: '50%'}}>
        {this.renderCards(key)}
      </div>
      {dataSet && <div className={classnames(styles.importPanel)} style={{ display: this.props.upload.panelVisible ? 'inline':'none'}}>
        <h2>Import Data Set From File</h2>
        {/*<h3>File：{file.name}</h3>*/}
        {/*<ImportPanel />*/}
      </div>}
    </div>
  }

  render () {
    return (
      <div>
        <div style={{ marginBottom: 20 }}>File List</div>
        <FileModal record={{}} refresh={() => this.fetchData()}>
          <Button type="primary" style={{ marginBottom: 20 }}>Upload</Button>
        </FileModal>
        <div className="cards">
          <Tabs defaultActiveKey="1">
            <TabPane tab="Private" key="1">{this.renderTabContent('owned_ds')}</TabPane>
            <TabPane tab="Public" key="2">{this.renderTabContent('public_ds')}</TabPane>
          </Tabs>
        </div>
      </div>
    )
  }

}

FileSystem.propTypes = {
  toDetail: PropTypes.func,
  dispatch: PropTypes.func,
}

export default connect(({ upload }) => ({ upload }))(FileSystem)
