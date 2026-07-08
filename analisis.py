from sqlalchemy import create_engine, text
from conexion import str_conexion
import pandas as pd



engine = create_engine(str_conexion)

consulta_transacciones = "SELECT * FROM transacciones"
consulta_categorias = "SELECT * FROM categorias"
consulta_usuarios = "SELECT * FROM usuarios WHERE activo = TRUE"

df_trans = pd.read_sql(consulta_transacciones, con=engine, parse_dates='fecha')
df_cat = pd.read_sql(consulta_categorias, con=engine)
df_users = pd.read_sql(consulta_usuarios, con=engine)

#REPORTE 1:
df_trans['mes'] = df_trans['fecha'].dt.to_period('M').dt.to_timestamp()

def obtener_balance_por_mes():
    df_reporte = pd.merge(df_trans, df_users, left_on='id_usuario', right_on='id', how='inner')
    df_reporte = (
        df_reporte.groupby(['id_usuario', 'nombre', 'mes', 'tipo_movimiento'])['monto'].sum()
        .unstack(fill_value=0)
        )
    
    df_reporte['balance'] = df_reporte['ingreso'] - df_reporte['gasto']
    df_reporte.columns.name=None

    return df_reporte

obtener_balance_por_mes()

#REPORTE 2
def obtener_montos_por_categoria():
    df_reporte = pd.merge(df_trans, df_cat, left_on='id_categoria', right_on='id', how='inner', suffixes=['_t', '_c'])
    df_reporte = (
        df_reporte.groupby(['id_usuario_t', 'mes', 'nombre_categoria', 'tipo_movimiento'])['monto'].sum()
        .unstack(fill_value=0)
        )
    
    df_reporte.columns.name=None

    return df_reporte

reporte_balance = obtener_balance_por_mes()
reporte_balance = reporte_balance.rename(columns={'ingreso': 'total_ingreso', 
                                'ahorro': 'total_ahorro',
                                'gasto': 'total_gasto'
                                }).reset_index()

reporte_por_categoria = obtener_montos_por_categoria()
reporte_por_categoria = reporte_por_categoria.reset_index().rename(columns={
    'ahorro': 'total_ahorro',
    'gasto': 'total_gasto',
    'ingreso': 'total_ingreso',
    'id_usuario_t': 'id_usuario'
    })

def load_a_sql(df_a_pasar, nombre_tabla):
    df_a_pasar.to_sql(
        name=nombre_tabla,
        con=engine,
        if_exists='append',
        index=False
    )

TABLAS_PERMITIDAS = ['reportes_mensuales', 'reportes_categorias']

def actualizar_tabla(df_a_pasar, nombre_tabla):

    if nombre_tabla not in TABLAS_PERMITIDAS:
        print('Tabla no permitida a borrar')
        return
    
    try:
        with engine.connect() as conexion:
            conexion.execute(text(f'DELETE FROM {nombre_tabla}'))
            conexion.commit()

            load_a_sql(df_a_pasar, nombre_tabla)
            print("Operación exitosa")
    except Exception as e:
        print(f'Error: {e}')
        conexion.rollback() 
    finally:
        conexion.close() 
    print('\n¡Traslado de datos completo!')

actualizar_tabla(reporte_balance, 'reportes_mensuales')
actualizar_tabla(reporte_por_categoria, 'reportes_categorias')