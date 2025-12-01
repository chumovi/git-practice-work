import pandas as pd
import numpy as np

source_meta = pd.read_csv('source_meta.csv')
registrations = pd.read_csv('registrations.csv')
conversions = pd.read_csv('conversions.csv')
clicks = pd.read_csv('clicks.csv')

# дефолтные метрики

clicks_count = clicks['client_id'].nunique()
registrations_count = registrations['client_id'].nunique()
conversions_count = conversions['client_id'].nunique()

cr_click_reg = (registrations_count / clicks_count) * 100
cr_reg_conv = (conversions_count / registrations_count) * 100
cr_click_conv = (conversions_count / clicks_count) * 100

basic_metrics_df = pd.DataFrame({
    'Метрика': [
        'CR Click → Reg',
        'CR Reg → Conv',
        'CR Click → Conv'
    ],
    'Значение': [

        f'{cr_click_reg:.2f}%',
        f'{cr_reg_conv:.2f}%',
        f'{cr_click_conv:.2f}%'
    ]
})

print("Метрика")
print(basic_metrics_df.to_string(index=False))
print()


# CR по источникам

print("CR by source")

clicks_by_source = clicks.groupby('source')['client_id'].nunique().reset_index()
clicks_by_source.columns = ['source', 'clicks']

clicks_cl_source = clicks[['client_id', 'source']].drop_duplicates()
regs_with_source = registrations.merge(clicks_cl_source,
                                       on='client_id', how='inner')
regs_by_source = regs_with_source.groupby('source')['client_id'].nunique().reset_index()
regs_by_source.columns = ['source', 'registrations']

convs_with_source = conversions.merge(clicks_cl_source,
                                      on='client_id', how='inner')
convs_by_source = convs_with_source.groupby('source')['client_id'].nunique().reset_index()
convs_by_source.columns = ['source', 'conversions']

source_metrics = (
    clicks_by_source
    .merge(regs_by_source,
           on='source', how='left')
    .merge(convs_by_source,
           on='source', how='left')
)

source_metrics = source_metrics.fillna(0)
source_metrics[['registrations', 'conversions']] = source_metrics[['registrations', 'conversions']].astype(int)

source_metrics['CR click-reg %'] = (source_metrics['registrations'] / source_metrics['clicks'] * 100).round(2)
source_metrics['CR reg-conv %'] = (
    (source_metrics['conversions'] / source_metrics['registrations'] * 100)
    .replace([np.inf, -np.inf], 0)
    .round(2)
)
source_metrics['CR click-conv %'] = (source_metrics['conversions'] / source_metrics['clicks'] * 100).round(2)

source_table = source_metrics[[
    'source', 'clicks', 'registrations', 'conversions',
    'CR click-reg %', 'CR reg-conv %', 'CR click-conv %'
]].copy()

source_table.columns = [
    'Source', 'Clicks', 'Registrations', 'Conversions',
    'CR click-reg %', 'CR reg-conv %', 'CR click-conv %'
]

print(source_table.to_string(index=False))
print()

source_table.to_csv('cr_by_source.csv', index=False)

# CR по ГЕО
print("CR by geo")

clicks_by_geo = clicks.groupby('geo')['client_id'].nunique().reset_index()
clicks_by_geo.columns = ['geo', 'clicks']

regs_by_geo = registrations.groupby('geo')['client_id'].nunique().reset_index()
regs_by_geo.columns = ['geo', 'registrations']

convs_with_geo = conversions.merge(registrations[['client_id', 'geo']],
                                   on='client_id', how='inner')
convs_by_geo = convs_with_geo.groupby('geo')['client_id'].nunique().reset_index()
convs_by_geo.columns = ['geo', 'conversions']

geo_metrics = (
    clicks_by_geo
    .merge(regs_by_geo,
           on='geo', how='left')
    .merge(convs_by_geo,
           on='geo', how='left')
)

geo_metrics = geo_metrics.fillna(0)
geo_metrics[['registrations', 'conversions']] = geo_metrics[['registrations', 'conversions']].astype(int)

geo_metrics['CR click-reg %'] = (geo_metrics['registrations'] / geo_metrics['clicks'] * 100).round(2)
geo_metrics['CR reg-conv %'] = (
    (geo_metrics['conversions'] / geo_metrics['registrations'] * 100)
    .replace([np.inf, -np.inf], 0)
    .round(2)
)
geo_metrics['CR click-conv %'] = (geo_metrics['conversions'] / geo_metrics['clicks'] * 100).round(2)

geo_table = geo_metrics[[
    'geo', 'clicks', 'registrations', 'conversions',
    'CR click-reg %', 'CR reg-conv %', 'CR click-conv %'
]].copy()

geo_table.columns = [
    'Geo', 'Clicks', 'Registrations', 'Conversions',
    'CR click-reg %', 'CR reg-conv %', 'CR click-conv %'
]

geo_table = geo_table.sort_values('CR click-conv %', ascending=False).reset_index(drop=True)

print(geo_table.to_string(index=False))
print()

geo_table.to_csv('cr_by_geo.csv', index=False)

print("XR by device")
clicks_by_device = clicks.groupby('device')['client_id'].nunique().reset_index()
clicks_by_device.columns = ['device', 'clicks']

clicks_client_device = clicks[['client_id', 'device']].drop_duplicates()

regs_with_device = registrations.merge(
    clicks_client_device,
    on='client_id',
    how='inner'
)
regs_by_device = regs_with_device.groupby('device')['client_id'].nunique().reset_index()
regs_by_device.columns = ['device', 'registrations']

convs_with_device = conversions.merge(
    clicks_client_device,
    on='client_id',
    how='inner'
)
convs_by_device = convs_with_device.groupby('device')['client_id'].nunique().reset_index()
convs_by_device.columns = ['device', 'conversions']

device_metrics = (
    clicks_by_device
    .merge(regs_by_device,
           on='device', how='left')
    .merge(convs_by_device,
           on='device', how='left')
)

device_metrics = device_metrics.fillna(0)
device_metrics[['registrations', 'conversions']] = (
    device_metrics[['registrations', 'conversions']].astype(int)
)

# ТВОИ названия колонок
device_metrics['CR click-reg %'] = (
    device_metrics['registrations'] / device_metrics['clicks'] * 100
).round(2)
device_metrics['CR reg-conv %'] = (
    (device_metrics['conversions'] / device_metrics['registrations'] * 100)
    .replace([np.inf, -np.inf], 0)
    .round(2)
)
device_metrics['CR click-conv %'] = (
    device_metrics['conversions'] / device_metrics['clicks'] * 100
).round(2)

device_table = device_metrics[[
    'device', 'clicks', 'registrations', 'conversions',
    'CR click-reg %', 'CR reg-conv %', 'CR click-conv %'
]].copy()

device_table.columns = [
    'Device', 'Clicks', 'Registrations', 'Conversions',
    'CR click-reg %', 'CR reg-conv %', 'CR click-conv %'
]

device_table = device_table.sort_values('CR click-conv %', ascending=False).reset_index(drop=True)

print(device_table.to_string(index=False))
print()

device_table.to_csv('cr_by_device.csv', index=False)
