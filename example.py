# -*- coding: utf-8 -*-
# put ThostFtdcApi to one of sys.path first
from ThostFtdcApiSOpt import CThostFtdcInputOrderField

try:
    import sys, ThostFtdcApiSOpt as api
    import traceback
except ModuleNotFoundError as exc:
    print(exc.msg)
    print("Please check the following path:")
    for path in sys.path:
        if not path:
            continue
        print(path)
    del path
    exit(1)
    pass

#Addr
FrontAddr="tcp://180.169.50.130:62715"
#LoginInfo
BROKERID="7080"
USERID="9920100024"
PASSWORD="888888"
APPID="client_LEE121_T1"
AUTHCODE="3WWJKJ"
#OrderInfo
INSTRUMENTID="130090003855"
PRICE=0.01
VOLUME=1
# DIRECTION=api.THOST_FTDC_D_Sell
DIRECTION=api.THOST_FTDC_D_Buy
#open
OFFSET="0"
#close
#OFFSET="1"

def ReqorderfieldInsert(tradeapi):
	print ("ReqOrderInsert Start")
	orderfield=api.CThostFtdcInputOrderField()
	orderfield.BrokerID=BROKERID
	orderfield.InstrumentID=INSTRUMENTID
	orderfield.UserID=USERID
	orderfield.InvestorID=USERID
	orderfield.Direction=DIRECTION
	orderfield.LimitPrice=PRICE
	orderfield.VolumeTotalOriginal=VOLUME
	orderfield.OrderPriceType=api.THOST_FTDC_OPT_LimitPrice
	orderfield.ContingentCondition = api.THOST_FTDC_CC_Immediately
	orderfield.TimeCondition = api.THOST_FTDC_TC_GFD
	orderfield.VolumeCondition = api.THOST_FTDC_VC_AV
	orderfield.CombHedgeFlag="1"
	orderfield.CombOffsetFlag=OFFSET
	orderfield.GTDDate=""
	orderfield.OrderRef="1"
	orderfield.MinVolume = 0
	orderfield.ForceCloseReason = api.THOST_FTDC_FCC_NotForceClose
	orderfield.IsAutoSuspend = 0
	tradeapi.ReqOrderInsert(orderfield,0)
	print ("ReqOrderInsert End")

def ReqQueryTrade(tradeapi):
	print("ReqQueryTrade Start")
	query_trade_field = api.CThostFtdcQryTradeField()
	query_trade_field.BrokerID = BROKERID
	query_trade_field.InvestorID = USERID
	query_trade_field.InstrumentID = INSTRUMENTID
	query_trade_field.ExchangeID = INSTRUMENTID
	# tradefield.TradeID = ""
	# tradefield.TradeTimeStart =
	tradeapi.ReqQryTrade(query_trade_field, 0)
	print("ReqQueryTrade End")

def ReqQryTradingAccount(tradeapi):
	print("ReqQryTradingAccount Start")
	trading_account_field = api.CThostFtdcTradingAccountField()
	trading_account_field.BrokerID = BROKERID
	trading_account_field.InvestorID = USERID
	trading_account_field.CurrencyID = "CNY"
	tradeapi.ReqQryTradingAccount(trading_account_field)
	print("ReqQryTradingAccount End")

def ReqQryOrder(tradeapi):
	print("ReqQryOrder Start")
	query_order_field = api.CThostFtdcQryOrderField()
	query_order_field.BrokerID = BROKERID
	query_order_field.InvestorID = USERID
	query_order_field.ExchangeID = INSTRUMENTID
	tradeapi.ReqQryOrder(query_order_field)
	print("ReqQryOrder End")



class CTradeSpi(api.CThostFtdcTraderSpi):
	tapi=''
	settlementInfo: bytearray
	def __init__(self,tapi):
		api.CThostFtdcTraderSpi.__init__(self)
		self.tapi=tapi
		
	def OnFrontConnected(self) -> "void":
		print ("OnFrontConnected")
		req_field = api.CThostFtdcReqAuthenticateField()
		req_field.UserID = USERID
		req_field.BrokerID = BROKERID
		req_field.AuthCode = AUTHCODE
		req_field.AppID = APPID
		req_field.UserProductInfo = "test"
		ret = self.tapi.ReqAuthenticate(req_field, 0)
		print(f"ret of reqAuth is {ret}")
  
		
  
	def OnRspAuthenticate(self, pRspAuthenticateField: 'CThostFtdcRspAuthenticateField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		if pRspInfo.ErrorID == 0:
			self.auth_staus = True
			print("交易服务器授权验证成功")
			loginfield = api.CThostFtdcReqUserLoginField()
			loginfield.BrokerID=BROKERID
			loginfield.UserID=USERID
			loginfield.Password=PASSWORD
			loginfield.UserProductInfo="python dll"
			self.tapi.ReqUserLogin(loginfield,0)
			print ("send login ok")
		else:
			print(f"交易服务器授权验证失败 {pRspInfo.ErrorMsg}")
		
	def OnRspUserLogin(self, pRspUserLogin: 'CThostFtdcRspUserLoginField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		print ("OnRspUserLogin")
		print ("TradingDay=",pRspUserLogin.TradingDay)
		print ("SessionID=",pRspUserLogin.SessionID)
		print ("ErrorID=",pRspInfo.ErrorID)
		print ("ErrorMsg=",pRspInfo.ErrorMsg)

  
		#  清空
		self.settlementInfo = bytearray()
		qryinfofield = api.CThostFtdcQrySettlementInfoField()
		qryinfofield.BrokerID=BROKERID
		qryinfofield.InvestorID=USERID
		qryinfofield.TradingDay=""
		self.tapi.ReqQrySettlementInfo(qryinfofield,0)
		print ("send ReqQrySettlementInfo ok")
		

	def OnRspQrySettlementInfo(self, pSettlementInfo: 'CThostFtdcSettlementInfoField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		if  pSettlementInfo is not None :
			try:
				self.settlementInfo.extend(pSettlementInfo.Content)
			except BaseException as e:
				traceback.print_exc()
		else :
			print ("content null")
		if bIsLast :
			pSettlementInfoConfirm=api.CThostFtdcSettlementInfoConfirmField()
			pSettlementInfoConfirm.BrokerID=BROKERID
			pSettlementInfoConfirm.InvestorID=USERID
			self.tapi.ReqSettlementInfoConfirm(pSettlementInfoConfirm,0)
			print ("send ReqSettlementInfoConfirm ok")
			
			s = self.settlementInfo.decode('GBK')
			print(f"settlementInfo: {s}")
   
		
	def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm: 'CThostFtdcSettlementInfoConfirmField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		print ("OnRspSettlementInfoConfirm")
		print ("ErrorID=",pRspInfo.ErrorID)
		print ("ErrorMsg=",pRspInfo.ErrorMsg)
		ReqorderfieldInsert(self.tapi)
		print ("send ReqorderfieldInsert ok")


	def OnRtnOrder(self, pOrder: 'CThostFtdcOrderField') -> "void":
		print ("OnRtnOrder")
		print ("OrderStatus=",pOrder.OrderStatus)
		print ("StatusMsg=",pOrder.StatusMsg)
		print ("LimitPrice=",pOrder.LimitPrice)
		
	def OnRspOrderInsert(self, pInputOrder: 'CThostFtdcInputOrderField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		print ("OnRspOrderInsert")
		print ("ErrorID=",pRspInfo.ErrorID)
		print ("ErrorMsg=",pRspInfo.ErrorMsg)


	def OnRspQryTrade(self, pTrade: "CThostFtdcTradeField", pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
		print("OnRspQryTrade")
		print("ErrorID",pRspInfo.ErrorID)
		print("ErrorMsg",pRspInfo.ErrorMsg)

	def OnRspQryTradingAccount(self, pTradingAccount: "CThostFtdcTradingAccountField", pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
		print("OnRspQryTradingAccount")
		print("ErrorID", pRspInfo.ErrorID)
		print("ErrorMsg", pRspInfo.ErrorMsg)

	def OnRspOrderAction(self, pInputOrderAction: "CThostFtdcInputOrderActionField", pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
		print("OnRspOrderAction")
		print("ErrorID", pRspInfo.ErrorID)
		print("ErrorMsg", pRspInfo.ErrorMsg)
		
def main():
	tradeapi=api.CThostFtdcTraderApi_CreateFtdcTraderApi()
	tradespi=CTradeSpi(tradeapi)
	tradeapi.RegisterSpi(tradespi)
	print(CTradeSpi.tapi)
	tradeapi.SubscribePrivateTopic(api.THOST_TERT_QUICK)
	tradeapi.SubscribePublicTopic(api.THOST_TERT_QUICK)
	tradeapi.RegisterFront(FrontAddr)	
	tradeapi.Init()
	tradeapi.Join()


	# 请求查询成交
	ReqQueryTrade(tradeapi)

	# 查询资金账户
	tradeapi.ReqQryTradingAccount()

	# 撤单
	tradeapi.ReqQrderAction()



	
if __name__ == '__main__':
	main()
