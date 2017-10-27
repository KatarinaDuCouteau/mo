import { request, config } from '../utils'

const { CORS, api } = config;
const { projectJobs, toolkits } = api;
const PREFIX = '/models';

// 获取用户所有models
export async function fetchModels(payload) {

  return await request(`${CORS}/project/jobs/${payload.projectId}?categories=${payload.categories}&status=200`);

}

// 首次 deploy model
export async function firstDeployModel(payload) {
  return await request(`${CORS}/served_model/deploy/${payload.jobID}`,
    {
      method: 'post',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
}
