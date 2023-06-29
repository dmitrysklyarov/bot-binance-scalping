//
//  StatisticsTableViewController.swift
//  Trade
//
//  Created by Dmitry Sklyarov on 20.06.2023.
//

import UIKit

class StatisticsTableViewController: UITableViewController {
    
    @IBOutlet weak var labelHourlyLast: UILabel!
    @IBOutlet weak var labelHourlyMax: UILabel!
    @IBOutlet weak var labelHourlyTotal: UILabel!
    @IBOutlet weak var labelDailyLast: UILabel!
    @IBOutlet weak var labelDailyMax: UILabel!
    @IBOutlet weak var labelDailyTotal: UILabel!
    @IBOutlet weak var labelWeeklyLast: UILabel!
    @IBOutlet weak var labelWeeklyMax: UILabel!
    @IBOutlet weak var labelWeeklyTotal: UILabel!
    @IBOutlet weak var viewHourly: UIView!
    @IBOutlet weak var viewDaily: UIView!
    @IBOutlet weak var viewWeekly: UIView!
    @IBOutlet weak var progressSymbol: UIProgressView!
    @IBOutlet weak var progressPrice: UIProgressView!
    @IBOutlet weak var labelBase: UILabel!
    @IBOutlet weak var labelQuote: UILabel!
    @IBOutlet weak var labelCurrentTime: UILabel!
    @IBOutlet weak var labelBottomPrice: UILabel!
    @IBOutlet weak var labelCurrentPrice: UILabel!
    @IBOutlet weak var labelTopPrice: UILabel!
    
    var urlSession = URLSession.shared
    var statisticsMain:StatisticsMain = StatisticsMain(bottomPrice: 0, currentPrice: 0, topPrice: 0, quote: 0, base: 0, baseInOrders: 0)

    override func viewDidLoad() {
        super.viewDidLoad()

        // Uncomment the following line to preserve selection between presentations
        // self.clearsSelectionOnViewWillAppear = false

        // Uncomment the following line to display an Edit button in the navigation bar for this view controller.
        // self.navigationItem.rightBarButtonItem = self.editButtonItem
        
        // create refreshControl
        let refreshControl = UIRefreshControl()

        // set refreshControl as table view's refreshControl
        self.refreshControl = refreshControl

        // set refresh control target and action
        refreshControl.addTarget(self, action: #selector(refreshData(_:)), for: .valueChanged)
        print("view")
    }
    
    @objc func refreshData(_ sender: Any) {
        // handle refreshing here
        fetchData()
        
        labelCurrentTime.text = GetCurrentTime()
        labelBottomPrice.text = Int2String(number:statisticsMain.bottomPrice)
        labelCurrentPrice.text = Int2String(number:statisticsMain.currentPrice)
        labelTopPrice.text = Int2String(number:statisticsMain.topPrice)
        labelBase.text = Int2String(number:statisticsMain.base)
        labelQuote.text = Int2String(number:statisticsMain.quote)
        
        progressPrice.progress = Float(statisticsMain.currentPrice - statisticsMain.bottomPrice) / Float(statisticsMain.topPrice - statisticsMain.bottomPrice)
        progressSymbol.progress = Float(statisticsMain.quote) / Float(statisticsMain.quote + statisticsMain.base)
        
        FillProgress(progressViews: viewHourly.subviews, profits: statisticsMain.hourlyProfit)
        FillProgress(progressViews: viewDaily.subviews, profits: statisticsMain.dailyProfit)
        FillProgress(progressViews: viewWeekly.subviews, profits: statisticsMain.weeklyProfit)
        
        FillProfit(last: labelHourlyLast, max: labelHourlyMax, total: labelHourlyTotal, profits: statisticsMain.hourlyProfit)
        FillProfit(last: labelDailyLast, max: labelDailyMax, total: labelDailyTotal, profits: statisticsMain.dailyProfit)
        FillProfit(last: labelWeeklyLast, max: labelWeeklyMax, total: labelWeeklyTotal, profits: statisticsMain.weeklyProfit)
        
        AddOrders(orders: statisticsMain.lastOrders)

        refreshControl?.endRefreshing()
    }
    
    func AddOrders(orders:[StatisticsOrder]){
        print("number of rows \(tableView.numberOfRows(inSection: 0))")
        for i in 4..<24{
            let indexPath = IndexPath(row: i, section: 0)
            guard let cell = tableView.cellForRow(at: indexPath) else { break }
            guard orders.indices.contains(i-4) else { break }
            let order:StatisticsOrder = orders[i-4]
            
            if let direction = cell.contentView.subviews[0] as? UILabel{
                direction.text = "\(order.direction) at: \(order.time)"
            }
            if let filled = cell.contentView.subviews[1] as? UILabel{
                filled.text = "filled: \(order.filled)"
            }
            if let price = cell.contentView.subviews[2] as? UILabel{
                price.text = "price: \(order.price)"
            }
            if let profit = cell.contentView.subviews[3] as? UILabel{
                profit.text = "profit: \(order.profit)"
            }

        }
    }
        
    func fetchData(){
        let url = "https://sklyarov.com/binance/statistics"
        let request = URLRequest(url:URL(string: url)!)
        let group = DispatchGroup()
        group.enter()
        let task = urlSession.dataTask(with: request){data,resp,err in
            defer {
                group.leave()
            }
            let statistic:StatisticsMain = try! JSONDecoder().decode(StatisticsMain.self, from: data!)
            self.statisticsMain = statistic
        }
        task.resume()
        group.wait()
    }
        
    func FillProfit(last:UILabel, max:UILabel, total:UILabel, profits:[Double]){
        last.text = String(round(profits[0] * 100) / 100)
        max.text = String(round(profits.max()! * 100) / 100)
        total.text = String(round(profits.reduce(0, +) * 100) / 100)
    }
    
    func FillProgress(progressViews:[UIView], profits:[Double]){
        let max = profits.max() ?? 1
        for i in 0...profits.count{
            guard i < progressViews.count else { break }
            if let v = progressViews[i] as? UIProgressView{
                if profits[i] < 0{
                    v.progressTintColor = UIColor.systemRed
                }
                else{
                    v.progressTintColor = UIColor.systemOrange
                }
                v.progress = Float(abs(profits[i]) / max)
            }
        }
    }
    
    func Int2String(number:Int)->String{
        let thousand = String(number / 1000)
        //thousand = String(repeating: "0", count: 2 - thousand.count) + thousand
        var one = String(number % 1000)
        one = String(repeating: "0", count: 3 - one.count) + one
        return "\(thousand) \(one)"
    }
    
    func GetCurrentTime()->String{
        let formatter = DateFormatter()
        formatter.timeStyle = .medium
        let now = Date()
        return formatter.string(from: now)
    }

    // MARK: - Table view data source

    /*
    override func numberOfSections(in tableView: UITableView) -> Int {
        // #warning Incomplete implementation, return the number of sections
        return 0
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        // #warning Incomplete implementation, return the number of rows
        return 0
    }
    */

    /*
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "reuseIdentifier", for: indexPath)

        // Configure the cell...

        return cell
    }
    */

    /*
    // Override to support conditional editing of the table view.
    override func tableView(_ tableView: UITableView, canEditRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the specified item to be editable.
        return true
    }
    */

    /*
    // Override to support editing the table view.
    override func tableView(_ tableView: UITableView, commit editingStyle: UITableViewCell.EditingStyle, forRowAt indexPath: IndexPath) {
        if editingStyle == .delete {
            // Delete the row from the data source
            tableView.deleteRows(at: [indexPath], with: .fade)
        } else if editingStyle == .insert {
            // Create a new instance of the appropriate class, insert it into the array, and add a new row to the table view
        }    
    }
    */

    /*
    // Override to support rearranging the table view.
    override func tableView(_ tableView: UITableView, moveRowAt fromIndexPath: IndexPath, to: IndexPath) {

    }
    */

    /*
    // Override to support conditional rearranging of the table view.
    override func tableView(_ tableView: UITableView, canMoveRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the item to be re-orderable.
        return true
    }
    */

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
