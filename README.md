


# Deploy

To deploy use the bash script created and pass the environment name

```bash
$ ./deploy.sh production

```

install requirements.txt
# install libs
rm -rf libs
mkdir -p libs/python/lib/python3.10/site-packages/
pip install -r requirements.txt --target libs/python/lib/python3.10/site-packages


## por que no en un Glue Job
por ejemplo La query demora 15 min, mientras corre y luego indicamos si fue satisfactorio o no
AWS Glue, you only pay for the time that your ETL job takes to run
$0.44 per DPU-Hour for each Python Shell job, billed per second, with a 1-minute minimum


30 queries diarios, cada uno demora 15 min
15*30*30 = 135000 minutos al mes = 225 horas

entonces estariamos pagando por un job mientras espera a que una query se ejecute, en un python shell
que solo se conecta, confirma resultado. al mes

0.0625 DPUs x 225 hours x 0.44 USD per DPU-Hour = 6.19 USD (Python shell ETL job cost)



20 ejecuciones diarias con 4 cambios de estado (start, execute query, get execution, end)

4 state transitions per workflow x 900 workflow requests = 3,600.00 state transitions per month
3,600.00 state transitions per month - 4000 Free Tier state transitions = -400.00 billable state transitions
Max (-400.00 billable state transitions, 0 ) = 0.00 billable state transitions per month
0.00 billable state transitions x 0.000025 USD per state transition = 0.00 USD per month
Standard Workflows pricing (monthly): 0.00 USD

Cada query demora 15 min

