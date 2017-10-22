import * as dataAnalysisService from '../services/dataAnalysis'
import * as stagingDataService from '../services/stagingData'
import * as modelService from '../services/model'
import { arrayToJson } from '../utils/JsonUtils'
import pathToRegexp from 'path-to-regexp'

export default {
  namespace: 'workBench',
  state: {
    //左侧
    isLeftSideBar: true,
    //用户拥有的 section
    sectionsJson: [],
    //现在开启的 section
    activeSectionsId: ['new_launcher ' + 'init'],
    //焦点位置section名称
    focusSectionsId: 'new_launcher ' + 'init',
    //加载状态
    loading: false,

    stagingDataList: [],

    project_id: '59c21ca6d845c0538f0fadd5',

    launchItems: [],

    algorithms: [],


  },
  reducers: {
    // 改变 left_side_bar
    toggleLeftSideBar(state, action) {
      return {
        ...state,
        isLeftSideBar: !state.isLeftSideBar,
      }
    },

    // 更新sections
    setSections(state, action) {
      return {
        ...state,
        sectionsJson: action.sectionsJson,
      }
    },

    // 添加一个 section
    addNewSection(state, action) {
      return {
        ...state,
        sectionsJson: {
          ...state.sectionsJson,
          [action.section['sectionId']]: action.section,
        },

      }
    },

    // 添加 active section, 将 focus 移到
    addActiveSection(state, action) {
      return {
        ...state,
        activeSectionsId: state.activeSectionsId.concat(action.sectionId),
        focusSectionsId: action.sectionId,
      }
    },

    // 关闭 active section
    removeActiveSection(state, action) {
      // 将 action.section_name 删掉
      return {
        ...state,
        activeSectionsId: state.activeSectionsId.filter(sectionId => sectionId !== action.sectionId),
      }
    },

    // 替换
    replaceActiveSection(state, action) {
      return {
        ...state,
        activeSectionsId: state.activeSectionsId
          .filter(sectionId => sectionId !== action.sectionId).concat(action.new_sectionId),
        focusSectionsId: action.sectionId,
      }
    },

    // 更新 active sections (看是否需要）
    setActiveSections(state, action) {
      return {
        ...state,
        activeSectionsId: action.activeSectionsId,
      }
    },

    // 切换 focus section
    setFocusSection(state, action) {
      return {
        ...state,
        focusSectionsId: action.focusSectionsId,
      }
    },

    // 改变 sections 好像不需要

    // 改变loading
    set_loading(state, action) {
      return {
        ...state,
        loading: action.loading,
      }
    },

    // 更改 stagingDataList
    setStagingDataList(state, action) {
      return {
        ...state,
        stagingDataList: action.stagingDataList,
      }
    },

    // 储存 algorithms
    setAlgorithms(state, action) {
      return {
        ...state,
        algorithms: action.payload.algorithms,
      }
    }

  },
  effects: {
    // 获取用户所有sections
    *fetchSections(action, { call, put }) {
      const { data: { [action.categories]: sections } } = yield call(dataAnalysisService.fetchSections, {
        projectId: action.projectId,
        categories: action.categories,
      });
      // array to json
      const sectionsJson = arrayToJson(sections, '_id');
      yield put({ type: 'setSections', sectionsJson })
    },
    *fetchAlgorithms(action, { call, put }) {
      const requestFunc = {
        toolkit: dataAnalysisService.fetchToolkits,
        model: modelService.fetchModels,
      };
      const { data: algorithms } = yield call(requestFunc[action.categories]);

      yield put({ type: 'setAlgorithms', payload: {algorithms: algorithms}})


    },
    // 更新用户 section
    *updateSection(action, { call, put, select }) {
      // 开始加载
      const sectionId = action.sectionId;
      const sectionsJson = yield select(state => state.dataAnalysis.sectionsJson)
      const section = sectionsJson[sectionId];
      const sections = yield call(dataAnalysisService.updateSection, sectionId, section)

      // 停止加载
      // 显示保存成功
      // yield put({type: 'setSections', sections})

    },

    // 添加 section
    *addSection(action, { call, put, select }) {
      //todo 1. 向后台发起请求 获得section 的json 内容
      const { data: section } = yield call(dataAnalysisService.addSection, action.section)
      // 2. 添加section
      yield put({ type: 'addNewSection', section: section })
      // 3. 替换原有active section
      yield put({
        type: 'replaceActiveSection',
        sectionId: action.section.sectionId,
        new_sectionId: section.sectionId,
      })
    },

    // 删除 section

    // 获取stage data set list
    *fetchStagingDatasetList(action, { call, put, select }) {
      const project_id = yield select(state => state.dataAnalysis.project_id)
      const { data: stagingDataList } = yield call(stagingDataService.fetchStagingDatas, project_id)
      yield put({ type: 'setStagingDataList', stagingDataList })

    },

  },
  subscriptions: {
    // 当进入该页面是 获取用户所有 section
    // setup({ dispatch, history }) {
    //   const pathJson = {
    //     analysis: 'toolkit',
    //     modelling: 'model',
    //   };
    //   return history.listen(({ pathname }) => {
    //     const match = pathToRegexp('/projects/:projectId/:categories').exec(pathname)
    //     if (match) {
    //       let projectId = match[1];
    //       let path = match[2];
    //       if (path in pathJson) {
    //         const categories = pathJson[path];
    //         dispatch({ type: 'fetchSections', projectId: projectId, categories })
    //         dispatch({ type: 'fetchAlgorithms', categories });
    //         dispatch({ type: 'fetchStagingDatasetList' });
    //       }
    //     }
    //   })
    // },
  },
}
