// http service for handling web requests

// constants

// api address
const api = 'http://3.23.61.95:8000/'

// http methods
const httpGet = 'GET'
const httpPost = 'POST'
const httpDelete = 'DELETE'
const httpPatch = 'PATCH'

// private variables and functions
var queryParams = (params) => {
  const keys = Object.keys(params)
  var queryStr = '?'
  for(var key of keys) {
    queryStr = `${queryStr}${key}=${params[key]}&`
  }
  return queryStr.slice(0, -1)
}
// make a full address from an endpoint path
var addr = (path, params) => {
  var url = `${api}${path}`
  if (params) {
    url = url+ queryParams(params)
  }
  return url
}

// turn an object into json
var json = (obj) => obj ? JSON.stringify(obj) : ''

//create request header object with auth token
var header = (notFile) => {
  var header = new Headers()
  if (notFile) {
    header = new Headers({'Content-Type':'application/json'})
  }
  var token = localStorage.getItem('token')
  if (token != null) {
    header.append('Authorization', ''.concat('Token ', token))
  }
  return header
}
// create the fetch() body
var body = (method, data) => ({method, headers: header(true), body: json(data)})

var fileBody = (method, data) => ({method, headers: header(false), body: data})

var getBody = (method) => ({method, headers: header(true)})
// service object
const httpService = {
  // GET request
  async get (path, params) { 
    var response = await fetch(addr(path, params), getBody(httpGet))
    if (response.status == 200) {
      var data = await response.json()
      return data
    }
    return false
  },
  // POST request
  post: async (path, data) => fetch(addr(path), body(httpPost, data)),

  filePost: async(path, data) => { 
    fetch(addr(path), fileBody(httpPost, data)) 
  },
  // DELETE request
  delete: async (path) => fetch(addr(path), body(httpDelete)),
  
  patch: async (path, data) => fetch(addr(path), body(httpPatch, data))

}

export default httpService
