import threading
def percent_rebalance(manager, order_style, timeout=60):
        print(f"Desired positions: ")
        for sym in manager.r_positions:
            print(f"{sym} - {manager.r_positions.get(sym)[0]} of portfolio.")
        print()

        positions = manager.api.list_positions()
        account = manager.api.get_account()
        portfolio_val = float(account.portfolio_value)
        for sym in manager.r_positions:
            price = manager.api.get_barset(sym, "minute", 1)[sym][0].c
            manager.r_positions[sym][0] = int(
                manager.format_percent(
                    manager.r_positions.get(sym)[0]) * portfolio_val / price)

        print(f"Current positions: ")
        for position in positions:
            print(
                f"{position.symbol} - {round(float(position.market_value) / portfolio_val * 100, 2)}% of portfolio.")
        print()

        manager.clear_orders()

        print("Clearing extraneous positions.")
        for position in positions:
            if(manager.r_positions.get(position.symbol)):
                manager.r_positions.get(position.symbol)[1] = int(position.qty)
            else:
                manager.send_basic_order(
                    position.symbol, position.qty, ("buy", "sell")[
                        position.side == "long"])
        print()

        if(order_style == "send"):
            for sym in manager.r_positions:
                qty = manager.r_positions.get(
                    sym)[0] - manager.r_positions.get(sym)[1]
                manager.send_basic_order(sym, qty, ("buy", "sell")[qty < 0])
        elif(order_style == "timeout"):
            threads = []
            for i, sym in enumerate(manager.r_positions):
                qty = manager.r_positions.get(
                    sym)[0] - manager.r_positions.get(sym)[1]
                threads.append(
                    threading.Thread(
                        target= manager.timeout_execution, args=(
                            sym, qty, ("buy", "sell")[
                                qty < 0], manager.r_positions.get(sym)[0], timeout)))
                threads[i].start()

            for i in range(len(threads)):
                threads[i].join()
        elif(order_style == "block"):
            threads = []
            for i, sym in enumerate(manager.r_positions):
                qty = manager.r_positions.get(
                    sym)[0] - manager.r_positions.get(sym)[1]
                threads.append(
                    threading.Thread(
                        target=manager.confirm_full_execution, args=(
                            sym, qty, ("buy", "sell")[
                                qty < 0], manager.r_positions.get(sym)[0])))
                threads[i].start()

            for i in range(len(threads)):
                threads[i].join()

def rebalance(manager, order_style, timeout=60):
        print(f"Desired positions: ")
        for sym in manager.r_positions:
            print(f"{sym} - {manager.r_positions.get(sym)[0]} shares.")
        print("\n")

        positions = manager.api.list_positions()

        print(f"Current positions: ")
        for position in positions:
            print(f"{position.symbol} - {position.qty} shares owned.")
        print()

        manager.clear_orders()

        print("Clearing extraneous positions.")
        for position in positions:
            if(manager.r_positions.get(position.symbol)):
                manager.r_positions[position.symbol][1] = int(position.qty)
            else:
                manager.send_basic_order(
                    position.symbol, position.qty, ("buy", "sell")[
                        position.side == "long"])
        print()

        if(order_style == "send"):
            for sym in manager.r_positions:
                qty = int(manager.r_positions.get(sym)[
                          0]) - manager.r_positions.get(sym)[1]
                manager.send_basic_order(sym, qty, ("buy", "sell")[qty < 0])
        elif(order_style == "timeout"):
            threads = []
            for i, sym in enumerate(manager.r_positions):
                qty = int(manager.r_positions.get(sym)[
                          0]) - manager.r_positions.get(sym)[1]
                threads.append(
                    threading.Thread(
                        target=manager.timeout_execution, args=(
                            sym, qty, ("buy", "sell")[
                                qty < 0], manager.r_positions.get(sym)[0], timeout)))
                threads[i].start()

            for i in range(len(threads)):
                threads[i].join()
        elif(order_style == "block"):
            threads = []
            for i, sym in enumerate(manager.r_positions):
                qty = int(manager.r_positions.get(sym)[
                          0]) - manager.r_positions.get(sym)[1]
                threads.append(
                    threading.Thread(
                        target=manager.confirm_full_execution, args=(
                            sym, qty, ("buy", "sell")[
                                qty < 0], manager.r_positions.get(sym)[0])))
                threads[i].start()

            for i in range(len(threads)):
                threads[i].join()