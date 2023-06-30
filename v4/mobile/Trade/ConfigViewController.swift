//
//  ConfigViewController.swift
//  Trade
//
//  Created by Dmitry Sklyarov on 22.06.2023.
//

import UIKit

class ConfigViewController: UIViewController {
    
    @IBOutlet weak var buttonLoad: UIButton!
    @IBOutlet weak var buttonSave: UIButton!
    
    @IBOutlet weak var sliderIndent: UISlider!
    @IBOutlet weak var sliderProfit: UISlider!
    @IBOutlet weak var sliderQuantity: UISlider!
    
    @IBOutlet weak var stepperIndent: UIStepper!
    @IBOutlet weak var stepperProfit: UIStepper!
    @IBOutlet weak var stepperQuantity: UIStepper!
    
    @IBOutlet weak var labelIndent: UILabel!    
    @IBOutlet weak var labelProfit: UILabel!
    @IBOutlet weak var labelQuantity: UILabel!
    
    var urlSession = URLSession.shared
    var config:Config? = nil
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
    }
    
    @IBAction func profitChanged(_ sender: Any) {
        sliderProfit.value = round(sliderProfit.value)
        if self.config == nil { return }
        self.config?.BTC.profit = String(sliderProfit.value)
        labelProfit.text = String(Int(sliderProfit.value))
        buttonLoad.isEnabled = true
    }
    
    @IBAction func indentChanged(_ sender: Any) {
        sliderIndent.value = round(sliderIndent.value)
        if self.config == nil { return }
        self.config?.BTC.indent = String(sliderIndent.value)
        labelIndent.text = String(Int(sliderIndent.value))
        buttonLoad.isEnabled = true
    }
    
    @IBAction func quantityChanged(_ sender: Any) {
        sliderQuantity.value = round(sliderQuantity.value * 10000)/10000
        if self.config == nil { return }
        labelQuantity.text = String(sliderQuantity.value)
        buttonLoad.isEnabled = true
    }
    

    @IBAction func loadClicked(_ sender: UIButton) {
        // Code to be executed when the button is clicked
        fetchData()
        guard let conf = self.config else {return}
        var base:ConfigBase
        switch conf.MAIN.base {
        case "BTC":
            base = conf.BTC
        case "ETH":
            base = conf.ETH
        default:
            return
        }
        labelIndent.text = String(base.indent)
        labelProfit.text = String(base.profit)
        labelQuantity.text = String(base.quantity)
        
        sliderIndent.minimumValue = Float(base.min_indent)!
        sliderIndent.maximumValue = Float(base.max_indent)!
        sliderIndent.value = Float(base.indent)!

        sliderProfit.minimumValue = Float(base.min_profit)!
        sliderProfit.maximumValue = Float(base.max_profit)!
        sliderProfit.value = Float(base.profit)!

        sliderQuantity.minimumValue = 0.0001
        sliderQuantity.maximumValue = 0.001
        sliderQuantity.value = Float(base.quantity)!
        
        buttonSave.isEnabled = true
        buttonLoad.isEnabled = false
    }

    @IBAction func saveClicked(_ sender: UIButton) {
        // Create the URL for the API endpoint
        guard let url = URL(string: "https://sklyarov.com/binance/set_config") else {
            return
        }

        // Create the PUT request
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        var jsonConfig = ""
        let encoder = JSONEncoder()
        encoder.outputFormatting = .withoutEscapingSlashes
        
        do {
            let jsonData = try encoder.encode(self.config)
            jsonConfig = String(data:jsonData, encoding: .utf8)!
        }
        catch{
            return
        }
        
        // Create the parameters dictionary
        let parameters = [
            "token": djangoToken,
            "config": jsonConfig
        ]

        // Set the request body with the parameters
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: parameters)
        } catch {
            print("Error encoding parameters: \(error)")
        }

        // Create a URLSession configuration
        let configuration = URLSessionConfiguration.default

        // Create a URLSession with the configuration
        let session = URLSession(configuration: configuration)

        // Create a data task with the request
        let task = session.dataTask(with: request) { (data, response, error) in
            if let error = error {
                print("Error: \(error)")
                return
            }

            // Process the response data here
            if let data = data {
                let responseString = String(data: data, encoding: .utf8)
                print("Response: \(responseString ?? "")")
            }
        }

        // Start the data task
        task.resume()

    }

    func fetchData(){
        let url = "https://sklyarov.com/binance/get_config"
        let request = URLRequest(url:URL(string: url)!)
        let group = DispatchGroup()
        group.enter()
        let task = urlSession.dataTask(with: request){data,resp,err in
            defer {
                group.leave()
            }
            let config:Config = try! JSONDecoder().decode(Config.self, from: data!)
            self.config = config
        }
        task.resume()
        group.wait()
    }


    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
