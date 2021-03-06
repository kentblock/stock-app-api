// service for managing portfolios and transactions for the current user

// constants

// private variables and functions
import httpService from './http.js'
// service object
const portfolioService = {

  async getPortfolios() {
    var portfolios = await httpService.get('api/portfolio/')
    return portfolios
  },
  async getPortfolio(id) {
    // get a portfolio by its id
    var portfolio = await httpService.get('api/portfolio/'.concat(id))
    return portfolio
  },
  async getHoldings(id) {
    //return holdings for a portfolio
    var holdings = await httpService.get('api/portfolio/'.concat(id, '/holdings'))
    return holdings
  },
  async newPortfolio(payload) {
    // make a new portfolio
    var response = await httpService.post('api/portfolio/', payload)
    var statusOk = response.status == 201 ? true : false
    return statusOk
  },
  async delPortfolio(portfolioId) {
    var response = await httpService.delete('api/portfolio/'.concat(portfolioId))
    return response
  },
  async getTransactions(portfolioId) {
    // return a list of transactions for a specific portfolio
    var transactions = await httpService.get('api/portfolio/'.concat(portfolioId, '/transaction'))
    return transactions
  },
  async newTransaction(payload, portfolioId) {
    // make a new transaction
    var response = await httpService.post('api/portfolio/'.concat(portfolioId, '/transaction'), payload)
    if (response.status == 201) {
      return 201
    }
    return response.json()
  },
}

export default portfolioService 