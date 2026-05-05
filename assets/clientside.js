window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.map = {
    move_marker: function(idx, store) {
        if (!store || !store.pos_x) return null;
        const el = document.querySelector('#g-map .js-plotly-plot');
        if (!el) return null;
        const i = Math.min(idx || 0, store.pos_x.length - 1);
        Plotly.restyle(el, { x: [[store.pos_x[i]]], y: [[store.pos_z[i]]] }, [1]);
        return null;
    }
};
