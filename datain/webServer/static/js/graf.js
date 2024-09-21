window.UUID = 0;
function genUUID($prefix='', suffix='') { return $prefix + ( ++UUID ).toString( )+suffix; }

class _logguer {
    constructor() {
        this._log = [];
    }
    log() {
        for (var i = 0; i < arguments.length; i++) {
            console.log(arguments[i]);
        }
    }
    title(_t, l=1) {
        if(l==1) {
            console.log('===== ', _t, ' =====');
        } else if(l==2) {
            console.log('==== ', _t, ' ====');
        } else if(l==3) {
            console.log('=== ', _t, ' ===');
        } else if(l==4) {
            console.log('== ', _t, ' ==');
        } else if(l==5) {
            console.log('= ', _t, ' =');
        } else {
            console.log('* ', _t, ' *');
        }
    }
    group(_fnc, _t={}) {
        console.group(_fnc + this.dictToStr(_t) );
    }
    groupEnd(_fnc, _t={}) {
        console.log('== END >' + _fnc + this.dictToStr(_t))
        console.groupEnd();
    }

    dictToStr(_t) {
        let tmp = []
        Object.keys(_t).forEach( (key) => { 
            tmp.push( key.toUpperCase() + ': ' + _t[key]); 
        });
        return ( tmp.length > 0 ? ' > ' + tmp.join(' > ') : '')
    }

    trace(_t) {
        this.log('TRACE: ', _t)
        console.log(_t.length)
        console.trace();
    }
}

var logguer = new _logguer();


class streamControl {
    constructor(_config) {
        let _default_config = {
            'prefix': 'stream_contol_',
            'onOpen':    () => {},
            'onMessage': (data) => {},
            'onClose':   () => {},
            'onError':   (error) => {},
        }

        this._config = { ..._default_config, ...config};
        this._uuid = genUUID(this._config['prefix']);
        this.socket = null;
        this.reconnectInterval = 5000; // Intentar reconectar cada 5 segundos
        this.isManualClose = false;    // Flag para evitar reconexiones cuando la desconexión es manual
        this.suscribe = {};
    }

    connect() {
        if (this.socket) { logguer.warn("WebSocket ya está conectado."); return; }

        this.socket = new WebSocket(this._config.uri.ws);
        // Evento cuando la conexión está abierta
        this.socket.onopen = () => { logguer.log("Conectado al WebSocket"); this.onOpen(); };
    
        // Evento cuando se recibe un mensaje
        this.socket.onmessage = (event) => { logguer.log("Mensaje recibido:", event.data); this.onMessage(event.data); };
    
        // Evento cuando la conexión se cierra
        this.socket.onclose = (event) => { logguer.log("Conexión cerrada:", event.reason || "Desconocido");
            this.onClose();
    
            if (!this.isManualClose) {
            logguer.log(`Intentando reconectar en ${this.reconnectInterval / 1000} segundos...`);
            setTimeout(() => this.connect(), this.reconnectInterval);
            }
        };
    
        // Evento cuando ocurre un error
        this.socket.onerror = (error) => { logguer.error("Error en el WebSocket:", error); this.onError(error); };
    }

    // Métodos que se pueden sobrescribir para manejar eventos
    onOpen() {
        // Personaliza la lógica cuando el WebSocket se conecta
    }

    onMessage(data) {
        // Personaliza la lógica cuando se recibe un mensaje
    }

    onClose() {
        // Personaliza la lógica cuando el WebSocket se cierra
    }

    onError(error) {
        // Personaliza la lógica cuando ocurre un error
    }

    send(message) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(message);
        } else {
            console.error("No se puede enviar el mensaje, WebSocket no está conectado.");
        }
    }

    addSuscribe(id, method, callback, status=false) {
        this.suscribe[id] = {
            status: status,
            method: method,
            callback: callback
        };
    }

    callSuscribe(data) {

    }

    suscribe(symbol, event, callback) {
        id = genUUID(symbol+'_'+event+'_');
        method = symbol+"@"+event

        a = {'id': id, 'method': method, 'params': []}
        this.send(JSON.stringify(a));

        this.addSuscribe(id, method, callback, true);
    }
}


class datasetBase {
    constructor(config={}) {
        let _default_config = {
            'prefix': 'dataset_base_',
        }
        this.config = { ..._default_config, ...config};

        this.name = this.config['name']
        this._uuid = genUUID(this.config['prefix'] + this.name);

        this._source = [];
        this._tramforms = {};
        this._series = {};
        this._dimensions = [];
    }

    getId()   { return this._uuid; }
    getName() { return this.name; }

    /**
     * @param {Array} d
     * @returns {void}
     */
    addSource(d) { this._source.push(d); }
    /**
     * @returns {Array}
     */
    getSource()  { return this._source; }

    /**
     * @param {tramformBase} tramform 
     */
    addTranform(tramform) { 
        this._tramforms[tramform.getId()] = tramform;
        tramform.setDatasetId(this.getId())
    }
    /**
     * @param {String} id 
     * @returns {null|tramformBase}
     */
    getTranform(id)  { return id in this._tramforms ? this._tramforms[id] : null; }

    /**
     * @returns {Object}
     */
    getTranforms()  { return this._tramforms; }

    getDatasetByName(n, interno=false) {
        if(n == this.getName())
            return this;
        for (let index of Object.keys(this._tramforms)) {

            let rs = this._tramforms[index].getDatasetByName(n, true);
            if(rs != null) return rs;
        }
        if(!interno) {
            console.error('datasetBase.getDatasetByName: not found', n);
        }
        return null;
    }

    /**
     * @returns {Array}
     */
    configDataset(rs=[]) {
        logguer.group('datasetBase.configDataset', { name: this.name, Id: this.getId() })
        logguer.groupEnd('datasetBase.configDataset: end', { name: this.name, Id: this.getId() })
        return rs;
    }

    /**
     * @returns {Array}
     */
    configDatasetTranforms(rs=[]) {
        logguer.group('datasetBase.configDataset._tramforms', { name: this.name, Id: this.getId() })
        Object.keys(this._tramforms).forEach( (key) => { this._tramforms[key].configDataset(rs); });
        logguer.groupEnd('datasetBase.configDataset._tramforms', { name: this.name, Id: this.getId() })
        return rs;
    }

    /**
     * @returns {Array}
     */
    configDatasets(rs=[]) {
        logguer.group('datasetBase.configDataset', { name: this.name, Id: this.getId() })

        rs = this.configDataset(rs);
        rs = this.configDatasetTranforms(rs);

        logguer.groupEnd('datasetBase.configDataset', { name: this.name, Id: this.getId() })
        return rs;
    }
}

class datasetTransformBase extends datasetBase {
    constructor(config) {
        let _default_config = {
            prefix: 'dataset_transform_base_',
        }
        config = { ..._default_config, ...config};
        super(config);
        this.name = this.config['prefix'] + this.config['name'];
        this._uuid = genUUID(this.name);

        this.fromDatasetId=null;
        this.config_transform = {};
    }
    setDatasetId(v) { this.fromDatasetId = v; }
    getDatasetId() { return this.fromDatasetId; }

    setConfigTransform(c) { this.config_transform = c; }
    getConfigTransform() { return this.config_transform; }

    configDataset(rs = []) {

        logguer.group('datasetTransformBase.configDataset', { name: this.name, Id: this.getId() })
        //logguer.trace(rs)
        rs.push({ 
            id:this._uuid, 
            sourceHeader: false,
            fromDatasetId: this.getDatasetId(),
            transform: this.getConfigTransform(),
            
        });
        logguer.log(rs)
        logguer.groupEnd('datasetTransformBase.configDataset', { name: this.name, Id: this.getId() })

        return super.configDataset(rs);
    }
}

class datasetKlineStream extends datasetBase {
    constructor(config) {
        let _default_config = {
            'prefix': 'dataset_kline_stream_',
            'name': 'binance',
            websocket: null
        }
        config = { ..._default_config, ...config};
        super(config);
        this.name = this.config['prefix'] + this.config['name'];
        this._uuid = genUUID(this.name);

        this.name = 'dataset_kline_stream';

        this.addTranform(new datasetTransformKline({name: 'kline'}));
        this.addTranform(new datasetTransformVolume({name: 'volume'}));
    }
    configDataset(rs=[]) {
        logguer.group('datasetKlineStream.configDataset', { name: this.name, Id: this.getId() })
        //logguer.trace(rs)
        rs.push( { 
            id:this._uuid, 
            sourceHeader: false,
            source: this.getSource(), 
            dimensions:[
                    { name: "time_open",          type:"time" },
                    { name: "time_close",         type:"time" },
                    { name: "symbol",             type:"ordinal" },
                    { name: "interval",           type:"ordinal" },
                    { name: "trade_first_id",     type:"number" },
                    { name: "trade_last_id",      type:"number" },
                    { name: "price_open",         type:"float" },
                    { name: "price_close",        type:"float" },
                    { name: "price_high",         type:"float" },
                    { name: "price_low",          type:"float" },
                    { name: "volume_base",        type:"float" },    // Base asset volume
                    { name: "trade_count",        type:"int" },
                    { name: "has_candle_close",   type:"ordinal" },
                    { name: "volume_quote",       type:"float" },    // Quote asset volume
                    { name: "volume_base_taker",  type:"float" },    // Taker buy base asset volume
                    { name: "volume_quote_taker", type:"float" },    // Taker buy quote asset volume
                    null,
            ]
        });
        logguer.log(rs)
        logguer.groupEnd('datasetKlineStream.configDataset', { name: this.name, Id: this.getId() })
        return super.configDataset(rs);
    }
}

class datasetTransformKline extends datasetTransformBase {
    constructor(config={}) {
        let _default_config = {}
        config = { ..._default_config, ...config};
        super(config);
        this.name = 'kline';
        this._uuid = genUUID('dataset_transform_kline_');
        this.setConfigTransform({ 
            type: 'kline_stream:volume', 
            config: { },
            print: true
        });

        //this.addSerie(new serieKline({}));
    }
}

class datasetTransformVolume extends datasetTransformBase {
    constructor(config={}) {
        let _default_config = {}
        config = { ..._default_config, ...config};
        super(config);
        this.name = 'volume';
        this._uuid = genUUID('dataset_transform_volume_');
        this.setConfigTransform({ 
            type: 'kline_stream:kline', 
            config: { },
            print: true
        });

        //this.addSerie(new serieVolume({}));
    }
}

const kline_stream_tranform = {
    utils_filter_cols:function(_cols, _data){
        let rs = [];
        for(let i=0; i<_data.length; i++){
            let _row = [];
            for(let j=0; j<_cols.length; j++){
                _row.push(_data[i][_cols[j]]);
            }
            rs.push(_row);
        }
        return rs;
    },
    kline:{
        type: 'kline_stream:kline',
        transform: function(params){
            let data = kline_stream_tranform.utils_filter_cols( ["t","o","c","h","l"], params.upstream.cloneRawData() )
            console.log(data);
            return [{
                dimensions: ["t","o","c","h","l"],
                data
            }];
        }
    },
    volume:{
        type: 'kline_stream:volume',
        transform: function(params){
            let data = kline_stream_tranform.utils_filter_cols( ["t","v"], params.upstream.cloneRawData() )
            console.log(data);
            return [{
                dimensions: ["t","v"],
                data
            }];
        }
    },
    trades:{
        type: 'kline_stream:trades',
        transform: function(params){
            let data = kline_stream_tranform.utils_filter_cols( ["t","f", "L", "n"], params.upstream.cloneRawData() )
            console.log(data);
            return [{
                dimensions: ["t","f", "L", "n"],
                data
            }];
        }
    }

};
echarts.registerTransform(kline_stream_tranform.kline);
echarts.registerTransform(kline_stream_tranform.volume);
echarts.registerTransform(kline_stream_tranform.trades);

class serieBase {
    constructor(_config) {
        this._uuid = genUUID('serie_' + (('name' in _config ? _config['name']+'_' : '')) );
        this._grid = null;
        this._dataset = null;

        let _default_config = {
            'name': 'serieBase',
        }

        this.addConfig({ ..._default_config, ..._config});
    }
    
    getId() { return this._uuid; }
    
    addConfig(_config) { this._config = _config }
    getConfig($k, $d=null) { return this._config[$k] || $d }

    setGrid(v) { this._grid = v; }
    getGrid() { return this._grid; }
    
    setDataset(v) { this._dataset = v; }
    getDataset() { return this._dataset; }

    configSerie(config={}) { 
        return { ...{
            id: this.getId(),
            name: this.getConfig('name'), 
            type: this.getConfig('type'), 
            datasetId: this.getDataset().getId(),
            xAxisId: this.getGrid().getXId(),
            yAxisId: this.getGrid().getYId(),
        }, ...config}
    }

    configVisualMap() { return null; }
}

class serieUtilVals extends serieBase {
    
    processData(d) {
        let rs=[];
        let _col_val = this.getConfig('_col_val');
        if(_col_val.length == 1) {
            if (d[_col_val[0]] != undefined) {
                rs = d[_col_val[0]]
            } else {
                rs = null
            }
        } else {
            for (let index = 0; index < _col_val.length; index++) {
                let key = _col_val[index];
                if (d[key] != undefined) {
                    rs.push(d[key])
                } else {
                    return null;
                }
            }
        }
        return rs;
    }
}

class serieKline extends serieBase {
    constructor(_config) {
        let _d_config = {
            name: 'Precio',
            type: 'candlestick',
            colors: {
                upColor: '#00da3c',
                downColor: '#ec0000',
                borderColor: undefined,
                borderColor0: undefined
            }
        }
        super({ ..._d_config, ..._config})
    }
    configSerie() {
        let colors =this.getConfig('colors');
        return super.configSerie({ 
            dimensions: ['date', 'open', 'close', 'highest', 'lowest'],
            itemStyle: { 
                color: colors.upColor, 
                color0: colors.downColor, 
                borderColor: colors.borderColor, 
                borderColor0: colors.borderColor0
            } 
        })
    }
}

class serieVolume extends serieUtilVals {
    constructor(_config) {
        let _d_config = {
            name: 'Volume',
            type: 'bar',
        }
        super({ ..._d_config, ..._config})
    }
    configSerie() {
        return super.configSerie({});
    }
}

class serieHeadmap extends serieBase {
    constructor(_config) {
        let _d_config = {
            name: 'headmap',
            type: 'heatmap',
            supra_type: 'yAxis',
            colors: {
                upColor: '#00da3c',
                downColor: '#ec0000',
                borderColor: undefined,
                borderColor0: undefined
            }
        }
        super({ ..._d_config, ..._config})
    }
    configVisualMap() { 
        return {
            seriesIndex: this.getSerieIndex(),
            min: 0,
            max: 100,
            precision: 2,
            calculable: true,
            realtime: false,
            inRange: {
                color: [
                    '#313695',
                    '#4575b4',
                    '#74add1',
                    '#abd9e9',
                    '#e0f3f8',
                    '#ffffbf',
                    '#fee090',
                    '#fdae61',
                    '#f46d43',
                    '#d73027',
                    '#a50026'
                ]
            }
        }

        ;
    }
    configSerie() {
        return { 
            id: this.getId(),
            type: this.getConfig('type'), 
            emphasis: {
                itemStyle: {
                    borderColor: '#333',
                    borderWidth: 1
                }
            },
            progressive: 1000,
            animation: false,
            datasetIndex: this.getDatasetIndex(),
            dimensions: ['date','price','qty'],
        };
    }
    configDataSet(data=[]) {
        let data_pross = [];
        for (let index = 0; index < data.length; index++) {
            data_pross = data_pross.concat(data[index]);
        }

        return { 
            id: this.getId(),
            sourceHeader: false,
            source: data_pross, 
        };
    }
    processDataTypeOne() { return false; }
    processData(d) {
        let rs=[];
        if('t' in d == false) return rs;
        if('bids' in d == false) return rs;
        if('asks' in d == false) return rs;


        for (let index = 0; index < d['bids'].length; index++) {
            rs.push( [d['t'], d['bids'][index][0], d['bids'][index][1]] );
            
        }
        for (let index = 0; index < d['asks'].length; index++) {
            rs.push( [d['t'], d['asks'][index][0], d['asks'][index][1]] );
            
        }

        return rs;
    }
}
class serieTime extends serieUtilVals {
    constructor(_config) {
        let _d_config = {
            type: 'category',
            supra_type: 'xAxis',
            _col_val: ['t']
        }
        super({ ..._d_config, ..._config})
    }
    getGrafConfig(data=[]) {
        return [
            {
                type: 'category',
                data: data,
                boundaryGap: false,
                axisLine: { onZero: false },
                splitLine: { show: false },
                min: 'dataMin',
                max: 'dataMax',
                axisPointer: {
                    z: 100
                }
            },
            {
                type: 'category',
                gridIndex: 1,
                data: data,
                boundaryGap: false,
                axisLine: { onZero: false },
                axisTick: { show: false },
                splitLine: { show: false },
                axisLabel: { show: false },
                min: 'dataMin',
                max: 'dataMax'
            }
        ];
    }

}

class grid {
    constructor(_config) {
        let _d_config = {
            'prefix': 'grid_default_',
            'name': '',
            'grid': {},
            'x': {},
            'y': {},
        }
        this._config = { ..._d_config, ..._config};
        this._uuid = genUUID(this._config['prefix']);
    }
    getId() { return this._uuid; }

    setTemplate(name, y_name='asd') { 
        if(name == 'principal') {
            let grid_id = this._uuid + '_principal_' +  this._config['name']
            let grid_x_id = grid_id + '_x'
            let grid_y_id = grid_id + '_y'
            this._config['grid'] = { id: grid_id, left: '0%', right: '5%', top: '0%',  height: '83%', containLabel: false, };
            this._config['x']    = { id: grid_x_id, type: 'time',                 gridId: grid_id,  boundaryGap: false, axisLine: { onZero: false }, splitLine: { show: false }, min: 'dataMin', max: 'dataMax', };
            this._config['y']    = { id: grid_y_id, type: "value", name: y_name,  gridId: grid_id, scale: true,  splitArea: { show: true }, position: 'right', min: (v) => { return v.min - (v.max - v.min) * 0.2; }, max: (v) => { return v.max + (v.max - v.min) * 0.2; }, }
        } else if(name == 'chica') {
            let grid_id = this._uuid + '_chica_' +  this._config['name']
            let grid_x_id = grid_id + '_x'
            let grid_y_id = grid_id + '_y'
            this._config['grid'] = { id: grid_id, left: '0%', right: '5%', top: '73%', height: '10%', containLabel: false, };
            this._config['x']    = { id: grid_x_id, type: 'time',                 gridId: grid_id,  boundaryGap: false, axisLine: { onZero: false }, splitLine: { show: false }, min: 'dataMin', max: 'dataMax', };
            this._config['y']    = { id: grid_y_id, type: "value", name: y_name,  gridId: grid_id, scale: true,  splitArea: { show: true }, position: 'right', min: (v) => { return v.min - (v.max - v.min) * 0.2; }, max: (v) => { return v.max + (v.max - v.min) * 0.2; }, }
        }
        return this;
    }
    
    getGridId() { return this._config['grid']['id'] }
    getConfigGrid() {
        return this._config['grid'];
    }
    
    getYId() { return this._config['y']['id'] }
    getConfigY() {
        return this._config['y'];
    }
    
    getXId() { return this._config['x']['id'] }
    getConfigX() {  
        return this._config['x'];
    }
}

class _graf {
    constructor(item, _config) {
        let _d_config = {
            title: '',
            datasets: {},
            series: {},
            grids: {},
        }
        this._config = { ..._d_config, ..._config};
        console.log(this._config)

        this.echarts_obj = null;
        this.dom_obj = dom_obj.get(0);
        this.generateEcharts();
    }

    getConfig($k, $d=null) {                        return $k in this._config ? this._config[$k] : $d; }
    setConfig($k, $v=null) { this._config[$k] = $v; return this._config[$k]; }
    addInConfig($config_k, $item_k, $v) {
        let tmp = this.getConfig($config_k, {});
        tmp[$item_k] = $v;
        this.setConfig($config_k, tmp);
    }
    getInConfig($config_k, $item_k, $d=null) {
        let tmp = this.getConfig($config_k, {});
        return $item_k in tmp ? tmp[$item_k] : $d;
    }
    
    addDataset(_v)  {        this.addInConfig('datasets', _v.getId(), _v); return this; }
    getDataset(_id) { return this.getInConfig('datasets', _id, null); }
    getDatasets()   { return this.getConfig('datasets', {}); }
    getDatasetsConfig() {
        let rs = [];
        let datasets = this.getDatasets();
        for (let index in datasets) {
            rs = datasets[index].configDatasets(rs)
        }
        return rs;
    }

    addGrid(_v)     {        this.addInConfig('grids', _v.getId(), _v); return this; }
    getGrid(_id)    { return this.getInConfig('grids', _id, null); }
    getGrids()      { return this.getConfig('grids', {}); }
    getGridsConfig() {
        let rs = [];
        let grids = this.getGrids();
        for (let index in grids) { rs.push(grids[index].getConfigGrid()) }
        return rs;
    }

    getGridsXConfig() {
        let rs = [];
        let grids = this.getGrids();
        for (let index in grids) { rs.push(grids[index].getConfigX()) }
        return rs;
    }

    getGridsYConfig() {
        let rs = [];
        let grids = this.getGrids();
        for (let index in grids) { rs.push(grids[index].getConfigY()) }
        return rs;
    }



    addSerie(_v)    {        this.addInConfig('series', _v.getId(), _v); return this; }
    getSerie(_id)   { return this.getInConfig('series', _id, null); }
    getSeries()     { return this.getConfig('series', {}); }
    getSeriesConfig() {
        let rs = [];
        let series = this.getSeries();
        for (let index in series) { rs.push(series[index].configSerie()) }
        return rs;
    }




    generateEcharts() {
        this.echarts_obj = echarts.init(
            this.dom_obj, 
            'dark', 
            { renderer: 'canvas', useDirtyRect: false }
        );
        window.addEventListener('resize', this.echarts_obj.resize);
    }

    loadOptions() {
        this.options = {
            animation: false,
            legend: { bottom: 10, left: 'center' },
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' },
                borderWidth: 1,
                borderColor: '#ccc',
                padding: 10,
                textStyle: { color: '#000' },
                position: function (pos, params, el, elRect, size) { const obj = { top: 10 }; obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30; return obj; }
                // extraCssText: 'width: 170px'
            },

            dataset: this.getDatasetsConfig(),

            // axisPointer: { link: [ { xAxisIndex: 'all' } ], label: { backgroundColor: '#777' } },
            // toolbox: { feature: { dataZoom: { yAxisIndex: false }, brush: { type: ['lineX', 'clear'] } } },
            // brush: { xAxisIndex: 'all', brushLink: 'all', outOfBrush: { colorAlpha: 0.1 } },
            visualMap: [
                //{ show: false, seriesIndex: 0, dimension: 2, pieces: [ { value: 1, color: '#ff0000' }, { value: -1, color: '#0000ff' } ] },
                //{ show: false, seriesIndex: 1, dimension: 2, pieces: [ { value: 1, color: '#ff0000' }, { value: -1, color: '#0000ff' } ] },
                
            ],
            grid: this.getGridsConfig(),
            xAxis: this.getGridsXConfig(),
            yAxis: this.getGridsYConfig(),
            series: this.getSeriesConfig(),
            // dataZoom: [
            //     { id: 'dataZoomXInside', type: 'inside', xAxisIndex: [0,1], show: true,          start: 0, end: 100 }, 
            //     { id: 'dataZoomXSlider', type: 'slider', xAxisIndex: [0, 1], top: '95%',          start: 0, end: 100 },
            //     { id: 'dataZoomYInside', type: 'inside', yAxisIndex: [0],   show: true,          start: 10, end: 90 }, 
            //     { id: 'dataZoomYSlider', type: 'slider', yAxisIndex: [0], start: 10, end: 90 },
            // ],
        };

        console.log(this.options)
        this.echarts_obj.setOption(this.options, true);
    }



    
    setLayerXAxis(_layer) { this._layers.xAxis = _layer; }
    addLayerYAxis(_layer) { 
        this._layers.yAxis.push(_layer);
    }

    loadSeries(items) {
        let times = [];

        for (let index_item = 0; index_item < items.length; index_item++) {

            let item = items[index_item];

            let key = this._layers.xAxis.processData(item);

            if(this._series[key] == undefined) {
                this._series[key] = {
                    xAxis: key,
                    yAxis: {},
                    data: [],
                };
            }

            this._series[key]['data'].push(item);

            for (let index_yAxis = 0; index_yAxis < this._layers.yAxis.length; index_yAxis++) {
                let _layer = this._layers.yAxis[index_yAxis] 
                let line = _layer.processData(item);

                if(line != null) {
                    if(_layer.processDataTypeOne()) {
                        this._series[key]['yAxis'][_layer.getId()] = line;
                    } else {
                        console.log(_layer.getConfig('type'))
                        console.log(line)
                        this._series[key]['yAxis'][_layer.getId()] = line;
                    }
                }

            }

        }
        //this.updateGraf();
    }
    updateGraf() {
        let update = {
            xAxis: [],
            visualMap: [],
            series: [],
            dataset: [],
        };

        tmp = {
            'x': [],
        };
        for (let i_serie in this._series) {
            const item = this._series[i_serie];
            tmp['x'].push(item['xAxis']);
            for (let layer_id in item['yAxis']) {
                const layer_data = item['yAxis'][layer_id];
                if (tmp[layer_id] == undefined) {
                    tmp[layer_id] = []
                }
                tmp[layer_id].push(layer_data)
            }
            
        }
        //console.log(tmp)
        
        // eje X
        //update['xAxis'] = this._layers.xAxis.getGrafConfig(tmp['x']);

        // DataSet
        // let _dataset = [];
        // for (let index = 0; index < this._layers.yAxis.length; index++) {
        //     _dataset.push( this._layers.yAxis[index].configDataSet(tmp[ this._layers.yAxis[index].getId() ]) );
        //     this._layers.yAxis[index].setDatasetIndex( _dataset.length -1 );
        // }

        // // Series
        // let _series = [];
        // for (let index = 0; index < this._layers.yAxis.length; index++) {
        //     _series.push(this._layers.yAxis[index].configSerie());
        //     this._layers.yAxis[index].setSerieIndex( _series.length -1 );
            
        // }

        // // VisualMap
        // let _visualMap = [];
        // for (let index = 0; index < this._layers.yAxis.length; index++) {
        //     let configVisualMap = this._layers.yAxis[index].configVisualMap()
        //     if(configVisualMap != null) {
        //         _visualMap.push(configVisualMap);
        //     }
        // }

        // if(_dataset.length > 0)    update.dataset = _dataset
        // if(_series.length > 0)     update.series = _series
        // if(_visualMap.length > 0)  update.visualMap = _visualMap

        
        // this.echarts_obj.setOption(update);
    }
}


(function($) {

    $.fn.graf = function(_options={}) {
        if($(this).data('_graf') == undefined) {
            dom_obj = $(this).eq(0);

            //dataset = new datasetKlineStream('asd', 'asd');
            //console.log(dataset.configSeries());
            //console.log(dataset.configDataset());
            //console.log(dataset.getSeries(true));

            

            tmp = new _graf(dom_obj, _options);
            tmp.loadOptions();
            $(this).data('_graf', tmp);
        }
        return $(this).data('_graf');
    }
})(jQuery)