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
