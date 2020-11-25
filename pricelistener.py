import statistics
import time

#
# based on theo moving up or down
#
# another iteration would be
# buy when theo > ask
# sell when theo < ask

class PriceListener:
    MAXRANGE = 250

    # number of standard deviations required 
    EDGE = 1.0
    UP   = '📈'
    DOWN = '📉'
    
    MIN_SAMPLES = 50

    def __init__(self):
        self.theo_buffer = []
        self.held_price = 0.0
        self.price_log = open('price_stat.log', 'w')


    def get_theo(self):
        return self.theo

    def on_price_update(self, bid, offer):
        self.theo = self.calc_theo(bid, offer)

        print("Theo = %0.2f" % self.theo)

        self.on_theo(self.theo)

    def on_theo(self, theo):
        self.theo_buffer.append(theo)

        if(len(self.theo_buffer) > self.MAXRANGE):
            self.theo_buffer = self.theo_buffer[1:self.MAXRANGE]

        self.check_price(theo)

    def check_price(self, theo):
        if(len(self.theo_buffer) > self.MIN_SAMPLES):
            mean_theo = statistics.mean(self.theo_buffer)
            sdev_theo = statistics.stdev(self.theo_buffer)

            print("mean = %f" % mean_theo)
            print("stdev = %f" % sdev_theo)

            if theo > self.held_price or theo > mean_theo:
                delta = (theo - self.held_price)/sdev_theo
                if delta > self.EDGE:
                    print('Looking BULLISH %s @%0.2f' % (self.UP, theo))
                    self.price_log.write('SELL, %f, %f, %f\n' % (time.time(), theo, delta))
                    self.held_price = theo
                else:
                    print('require price >= %0.2f' % (theo+(sdev_theo*self.EDGE)))
                    print('sell delta = %f' % delta)
            else:
                if theo < self.held_price or theo < mean_theo:
                    delta = (mean_theo - theo)/sdev_theo
                    if delta > self.EDGE:
                        print('Looking BEARISH %s @%0.2f' % (self.DOWN, theo))
                        self.price_log.write('BUY, %f, %f, %f\n' % (time.time(), theo, delta))
                        self.held_price = theo
                    else:
                        print('require price >= %0.2f' % (theo-(sdev_theo*self.EDGE)))
                        print('buy delta = %f' % delta)
                        
            self.price_log.flush()
        
    def calc_theo(self, bid, offer):

        weighted_price = 0.0
        total_volume = 0.0

        for level in bid:
            weighted_price += float(level[0])*float(level[1])
            total_volume += float(level[1])
        
        for level in offer:
            weighted_price += float(level[0])*float(level[1])
            total_volume += float(level[1])

        if total_volume > 0.0:
            return weighted_price / total_volume

        return 0.0
        
    
    
