from flask import Flask, render_template, request, jsonify
import json
import os
import btcData
import btcTransaction
import random

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


#Webpages
@app.route('/')
@app.route('/dashboard')
def dashboard():
    path = os.path.join(app.root_path, 'data', 'activePlan.json')
    with open(path, 'r') as file:
        plans = json.load(file)
    
    path = os.path.join(app.root_path, 'data', 'account.json')
    with open(path, 'r') as file:
        account = json.load(file)

    holding = btcTransaction.getHolding()
    holdingOrice = btcTransaction.getPrice(holding)
    currentPrice = btcData.getCurrentPrice()

    return render_template('dashboard.html', plans=plans, holding=holding, holdingOrice=holdingOrice, currentPrice=currentPrice, account=account)

@app.route('/strategies')
def strategies():
    path = os.path.join(app.root_path, 'data', 'strategy.json')
    with open(path, 'r') as file:
        strategy = json.load(file)
    path = os.path.join(app.root_path, 'data', 'account.json')

    with open(path, 'r') as file:
        account = json.load(file)

    return render_template('strategies.html', strategy=strategy, account=account)
    
@app.route('/setting')
def setting():
    path = os.path.join(app.root_path, 'data', 'account.json')
    with open(path, 'r') as file:
        account = json.load(file)


    return render_template('setting.html', account=account)
#Webpages

#Reserved for dashborad
#@app.route('/currentPrice')
#def market_price():
#    currentPrice = btcData.getCurrentPrice()
#    return jsonify({'currentPrice': currentPrice})

#Strategy
@app.route('/update_strategy', methods=['POST'])
def update_strategy():
    if request.method == 'POST':
        strategy_data = request.json

        # Update strategy.json
        path = os.path.join(app.root_path, 'data', 'strategy.json')
        with open(path, 'r+') as file:
            strategies = json.load(file)
            for strategy in strategies:
                if strategy['name'] == strategy_data['name']:
                    strategy['code'] = strategy_data['code']
                    break

            file.seek(0)  # Move cursor to  beginning
            json.dump(strategies, file, indent=4)  # Write updated strategies
            file.truncate()  # Prevents data overflow

        try:
            downloadScript()
            return jsonify({'message': 'Strategy updated successfully'}), 200
        except Exception as e:
            return jsonify({'error': f'Failed to generate scripts: {e}'}), 500
    else:
        return jsonify({'error': 'Invalid request method'}), 400


def downloadScript():
    print("downloadScript")
    path = os.path.join(app.root_path, 'data', 'strategy.json')
    with open(path) as f:
        strategies = json.load(f)

    for strategy in strategies:
        name = strategy['name']
        code = strategy['code']
        script_path = os.path.join("app", f'{name}.py')
        with open(script_path, 'w') as script_file:
            script_file.write(code)
    print("downloadScript")










#Plan Action
#Plan detail for ajax
@app.route('/getPlanDetail')
def getPlanDetail():
    name = request.args.get('name')
    path = os.path.join(app.root_path, 'data', 'activePlan.json')
    with open(path, 'r') as file:
        plans = json.load(file)
        for plan in plans:
            if plan['name'] == name:
                return jsonify(plan)

    return jsonify({'error': 'Plan not found'})

#Create new plan
@app.route('/newPlan', methods=['POST'])
def newPlan():
    if request.method == 'POST':
        data = request.json
        path = os.path.join(app.root_path, 'data', 'activePlan.json')
        with open(path, 'r+') as file:
            plans = json.load(file)

            new_plan = {
                "name": data['planName'],
                "initAmount": data['initialAmount'],
                "Balance": data['initialAmount'],
                "Holding": 0,
                "strategy": data['strategy']
            }
            plans.append(new_plan)
            file.seek(0)
            json.dump(plans, file, indent=4)
            file.truncate()

        try:
            btcTransaction.setBalance(btcTransaction.getBalance()-data['initialAmount'])
            return jsonify({'message': 'Plan created successfully'}), 200
        except Exception as e:
            return jsonify({'error': f'Failed to create plan: {e}'}), 500
    else:
        return jsonify({'error': 'Invalid request method'}), 400
    
#Exit Plan
@app.route('/exitPlan')
def exitPlan():
    name = request.args.get('name')
    print("Plan deleted: " + name)
    active_plan_path = os.path.join(app.root_path, 'data', 'activePlan.json')
    with open(active_plan_path, 'r+') as active_file:
        active_plans = json.load(active_file)
        updated_plans = [plan for plan in active_plans if plan['name'] != name]
        
        active_file.seek(0)
        json.dump(updated_plans, active_file, indent=4)
        active_file.truncate()

    return jsonify({'message': f'Exit action performed for plan {name}'})

@app.route('/sellPlan')
def sellPlan(name):
    factor = random.randint(70000, 80000)    
    path = os.path.join(app.root_path, 'data', 'activePlan.json')
    with open(path, 'r+') as file:
        plans = json.load(file)
        for plan in plans:
            if plan['name'] == name:
                plan['Balance'] = plan['Holding'] * factor
                plan['Holding'] = 0
        
        file.seek(0)
        json.dump(plans, file, indent=4)
        file.truncate()

    btcTransaction.setBalance(btcTransaction.getBalance()+plans['Balance'])
#Plan Action


#Simulate transaction
@app.route('/frame')
def frame():
    simulate()
    return "Simulation trade completed"

def simulate():
    
    #factor = btcData.getCurrentPrice() #For real use sing real data
    
    factor = random.randint(70000, 80000) #For beta testing
    
    
    path = os.path.join(app.root_path, 'data', 'activePlan.json')
    with open(path, 'r+') as file:
        plans = json.load(file)
        for plan in plans:
            if plan['Holding'] == 0:
                plan['Holding'] = plan['Balance'] * (1/factor)
                plan['Balance'] = 0
            elif plan['Balance'] == 0:
                plan['Balance'] = plan['Holding'] * factor
                plan['Holding'] = 0
        
        file.seek(0)
        json.dump(plans, file, indent=4)
        file.truncate()



#Start Hosting
if __name__ == "__main__":
    app.run(debug=True)

