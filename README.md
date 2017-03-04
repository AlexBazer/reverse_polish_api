## Reverse polish notation calculator API

### Before run

ZeroMQ binaries should be installed into the system.
For **Ubuntu** ```sudo apt-get install libzmq-dev```

Install pip requirements

### Local run

``` python main.py ```

### API Description

#### Request

```
{
    "expressions":
        [ (string): <list of expressions> ]
}
```

#### Response with status OK
```
{
    "status": "OK",
        "results":[
            {
                "expression" (string): assigned expression
                "result" (string): calculation result
                "time" (string): calculation time
            }
    ]
}
```

#### Response with status ERROR
```
{
    "status": "ERROR",
    "msg" (string): Error message
}
```

**OR**
```
{
    "status": "ERROR",
        "results":[
            {
                "expression" (string): assigned expression
                "result" (string): calculation error message
                "time" (string): calculation time
            }
    ]
}
```
