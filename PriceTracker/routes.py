from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from models import User, Symbol
import yfinance as yf

def routes(app, db, bcrypt):
    
    @app.route('/')
    def check():
        if current_user.is_authenticated:
            redirect(url_for('home'))
        return redirect(url_for('login'))
    
    @app.route('/home')
    @login_required
    def home():
        tickers = Symbol.query.filter_by(user_id=current_user.uid).all()

        return render_template('home.html', tickers=tickers)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username has already been taken')
                return redirect(url_for('register'))
            
            hashed_password = bcrypt.generate_password_hash(password)
            user = User(username=username, password=hashed_password)

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('login'))
        
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter(User.username == username).first()

            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            
            flash("Invalid username or password!")
             
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))
    
    @app.route('/get_ticker_data', methods=['POST'])
    def get_ticker_data():
        ticker = request.get_json()['ticker']
        data = yf.Ticker(ticker).history(period='1d')
        return jsonify({'currentPrice': data.iloc[-1].Close,
                        'openPrice': data.iloc[-1].Open,
                        'volume': data.iloc[-1].Volume})
    
    @app.route('/add_ticker', methods=['POST'])
    def add_ticker():
        symbol = request.form.get('add-ticker')
        data = yf.Ticker(symbol).history(period='1d')
        if data.empty:
            return jsonify({'status': 'error',
                            'message': f'Invalid ticker symbol: {symbol}'})
        elif db.session.query(Symbol.id).filter_by(name=symbol, user_id=current_user.uid).scalar() is not None:
            return jsonify({'status': 'error',
                            'message': f'Symbol already exists: {symbol}'})
        else:
            new_ticker = Symbol(name=symbol, user=current_user)
            db.session.add(new_ticker)
            db.session.commit()

            return jsonify({'id': new_ticker.id, 
                            'symbol': new_ticker.name})
    
    @app.route('/remove_ticker/<ticker>', methods=['POST'])
    def remove_ticker(ticker):
        symbol = Symbol.query.filter_by(name=ticker, user_id=current_user.uid).first()
        
        db.session.delete(symbol)
        db.session.commit()

        return jsonify({'status': 'success'})
    
    @app.route('/remove_all_tickers', methods=['POST'])
    def remove_all_tickers():
        Symbol.query.filter_by(user_id=current_user.uid).delete()
        db.session.commit()

        return jsonify({'message': 'All tickers removed successfully!'})
    
    @app.route('/get_all_symbols')
    def get_all_symbols():
        symbols = Symbol.query.filter_by(user_id=current_user.uid).all()
        symbol_names = [symbol.name for symbol in symbols]
        
        return jsonify(symbol_names)