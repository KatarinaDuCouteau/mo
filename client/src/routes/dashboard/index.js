import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'dva'
import { FileSystem } from './components';
import styles from './index.less'
import { color } from '../../utils'

const bodyStyle = {
  bodyStyle: {
    height: 432,
    background: '#fff',
  },
};

function Dashboard ({ dashboard }) {
  return(
    <div style={bodyStyle}>
      <FileSystem/>
    </div>
  )
}

Dashboard.propTypes = {
  dashboard: PropTypes.object,
};

export default connect(({ dashboard }) => ({ dashboard }))(Dashboard)
