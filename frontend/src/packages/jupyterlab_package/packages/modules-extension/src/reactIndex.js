import * as React from 'react'
import { Card, Button, Row, Col, Input } from 'antd'

import {
  VDomRenderer
} from '@jupyterlab/apputils';

import {
  NotebookActions,
} from '@jupyterlab/notebook'

import ParamsMapper from './ParamsMapper'

import { getModules, getModule, getProjects } from './services'

function genConf(args) {
  return JSON.stringify(args).replace(/'/g, '`')
}

const Search = Input.Search

const type = 'module'
const privacy = 'public'

export
class ModulePage extends React.Component {

  constructor() {
    super()
    this.state = {
      projects: [],
    }
  }

  componentDidMount() {
    this.fetchData({})
  }

  fetchData({ payload }) {
    let filter = { type, privacy };
    ['query', 'privacy'].forEach((key) => {
      if (this.state[key]) {
        filter[key] = this.stats[key]
      }
    })
    if (payload) {
      for (let key in payload) {
        if (!payload.hasOwnProperty(key)) {
          continue
        }
        if (payload[key]) {
          filter[key] = payload[key]
          this.setState({
            key: payload[key],
          })
        }
      }
    }
    getProjects({
      filter,
      onJson: (projects) => this.setState({
        projects,
      })
    })
  }

  onModuleSuccess = (response, func) => {
    this.setState({
      projectId: response._id,
      project: response,
      func: func,
      args: Object.values(response.args[func]),
    })
  }

  clickProject(project, func) {
    getModule({ projectId: project._id }, (response) => this.onModuleSuccess(response, func))
  }

  backToList(project) {
    this.setState({
      projectId: undefined,
      project: undefined,
      func: undefined,
      args: undefined,
    })
  }

  handleQueryChange(value) {
    this.fetchData({ payload: { query: value } })
  }

  insertCode() {
    const user_ID = localStorage.getItem('user_ID')
    NotebookActions.insertCode(this.props.tracker.currentWidget.notebook,
      [
        `conf = '${genConf(this.state.args)}'\n`,
        `conf = json_parser(conf)\n`,
        `result = ${this.state.func}('${user_ID}/${this.state.project.name}', conf)\n`,
      ],
    )
  }

  setValue(values) {
    let args = this.state.args
    for (let key in values) {
      let idx = args.findIndex(e => e.name === key)
      if (Array.isArray(values)) {
        args[idx].values = values[key]
      } else {
        args[idx].value = values[key]
      }
    }
    this.setState({
      args,
    })
  }

  renderParameters() {
    return (
      <div>
        <ParamsMapper args={this.state.args}
                      setValue={(values) => this.setValue(values)}
                      baseArgs={Object.values(this.state.project.args[this.state.func])}
        />
      </div>
    )
  }

  render() {
    if (this.state.projectId !== undefined) {
      return (
        <div style={{ minHeight: 100, overflowY: 'auto' }}>
          <h2>{this.state.project.name}</h2>
          {this.renderParameters()}
          <Row>
            <Button type='primary' onClick={() => this.insertCode()}>Insert Code</Button>
            <Button onClick={() => this.backToList()}>Cancel</Button>
          </Row>
        </div>
      )
    } else {
      return (
        <div style={{ height: '100%' }}>
          <header>MODULE LIST</header>
          <Search
            placeholder="input search text"
            onSearch={(value) => this.handleQueryChange(value)}
          />
          <div className='list'>
          {this.state.projects.map((project) =>
            <Card key={project.name} title={project.name}
              // onClick={() => this.clickModule(project)}
                  style={{ margin: '5px 3px', cursor: 'pointer' }}>
              <Col>
                {project.description}
                <Row>
                  <Button onClick={() => this.clickProject(project, 'train')}>train</Button>
                  <Button onClick={() => this.clickProject(project, 'predict')}>predict</Button>
                </Row>
              </Col>
            </Card>)}
          </div>
        </div>
      )
    }
  }

}

