//
//  Models.swift
//  Trade
//
//  Created by Dmitry Sklyarov on 20.06.2023.
//

import Foundation

struct StatisticsMain : Codable{
    var bottomPrice:Int
    var currentPrice:Int
    var topPrice:Int
    var quote:Int
    var base:Int
    var baseInOrders:Int
    var hourlyProfit = [Double]()
    var dailyProfit = [Double]()
    var weeklyProfit = [Double]()
    var lastOrders = [StatisticsOrder]()
}

struct StatisticsOrder : Codable{
    var direction:String
    var time:String
    var filled:Double
    var price:Int
    var profit:Double
}

struct Config : Codable{
    var MAIN:ConfigMain
    var BTC:ConfigBase
    var ETH:ConfigBase
}

struct ConfigMain : Codable{
    var base:String
    var quote:String
    var wait:String
}

struct ConfigBase : Codable{
    var quantity:String
    var step:String
    var indent:String
    var min_indent:String
    var max_indent:String
    var profit:String
    var min_profit:String
    var max_profit:String
    var commission:String
}
