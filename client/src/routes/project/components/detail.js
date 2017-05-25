import React from 'react';
import PropTypes from 'prop-types';
import { Button, Select } from 'antd';
import {jupyterServer } from '../../../constants';
import { Router , routerRedux} from 'dva/router';
import Jupyter from 'react-jupyter';


export default class ProjectDetail extends React.Component {
  constructor(props) {
    super(props);
    let name = this.getProjectName();
    this.state = {
      projectName: name,
      flieList: [],
      notebookName: '',
      notebookJSON: {
        "cells": [],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 2
      }
    }
  }

  getProjectName(){
    let path = location.pathname;
    let temp = path.split('/');
    return temp[2];
  }


  componentDidMount() {

    fetch(jupyterServer + this.state.projectName, {
      method: 'get'
    }).then((response) => response.json())
      .then((res) => {
        this.setState({
          fileList: res.content
        });
        let content = res.content;
        content.forEach((e) => {
          let el = e.name.split(".");
          if (el[1] === "ipynb") {
            console.log(e.name);
            fetch(jupyterServer + this.state.projectName +'/' + e.name, {
              method: 'get'
            }).then((response) => response.json())
              .then((res) => {
                  this.setState({notebookJSON: res.content});
              })
          }
        });
      });
  }

  handleClick() {
  }

  renderList() {
    let files = this.state.fileList;
    console.log(files);
    if(files) {
      return files.map((e) =>
        <div style={{margin: '5px 10px 5px 20px'}} key={e.name}>{e.name}</div>
      );
    }else{
      return null
    }
  }


  render() {
    return (
      <div className="content-inner">
        <div>
          <div >
            <h1>{this.state.projectName}</h1>
            <Button type='primary' style={{marginTop: 10}}
                    onClick={() => this.handleClick()}>Start Exploring</Button>
          </div>
          <div style={{marginTop: 20, display: 'flex', flexDirection: 'row'}}>
            <div style={{width: '40%', height: 700, border: '1px solid #f3f3f3'}}>
              <h3 style = {{margin: '5px 5px 5px 10px'}}>File List</h3>
              {this.renderList()}
              <h3 style = {{margin: '5px 5px 5px 10px'}}>Data List</h3>
            </div>
            <div style={{width: '59%', height: 700, marginLeft: '2%', border: '1px solid #f3f3f3'}}>
              <h3 style = {{margin: '5px 5px 5px 10px'}}>Previous Results</h3>
              <div style ={{paddingLeft: 70, paddingTop: 20}}>
                <Jupyter
                  notebook={this.state.notebookJSON}
                  showCode={true} // optional
                  defaultStyle={true} // optional
                  loadMathjax={true} // optional
                />
            </div>
            </div>
          </div>

        </div>
      </div>
    );
  }
}

ProjectDetail.propTypes = {
  toEdit: PropTypes.func,
}