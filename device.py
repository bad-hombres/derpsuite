import frida
import time

session = None

def init():
    global session
    if session == None:
        session = frida.get_usb_device()

def id():
    init()
    return session.id

def name():
    init()
    return session.name

ENUM_CLASSES = """
setImmediate(function() {
    Java.perform(function() {
        Java.enumerateLoadedClasses({
          "onMatch": function(aMatch) {
            send(aMatch);
          },
          "onComplete": function() {
          }
        });
        send("FINISHED")
    });
});
"""

ENUM_METHOD = """
setImmediate(function() {
    Java.perform(function() {
        var targetClass = "%s";
        var hook = Java.use(targetClass);
        var methods = hook.class.getDeclaredMethods();
        hook.$dispose();
        methods.forEach(function(m) {
            send(m.toString().replace(targetClass + ".", "TOKEN").match(/\\sTOKEN(.*)\(/)[1]);
        });
        send("FINISHED");
    });
});
"""

FINISHED=False
RESULTS=[]
METHODs=[]

proc = None

def enum_processes():
    init()
    return map(lambda x: x.name, session.enumerate_processes())

def on_message(message, data):
    global FINISHED
    global RESULTS
    if "payload" in message:
        if message["payload"] == u"FINISHED":
            FINISHED = True
        else:
            RESULTS.append(message["payload"])


def _enum_stuff(name, script_text):
    global FINISHED
    global RESULTS
    global proc

    RESULTS=[]
    FINISHED=False
    init()
        
    script = proc.create_script(script_text)
    script.on("message", on_message)
    script.load()
    while not FINISHED:
        print "Sleeping....zzzzzz" + str(FINISHED)
        time.sleep(0.5)

    script.unload()
    return list(set(RESULTS))

def enum_classes(process):
    global proc

    if not proc == None:
        proc.detach()
    proc = session.attach(process)

    return _enum_stuff(process, ENUM_CLASSES)

def enum_methods(class_name):
    return _enum_stuff(class_name, ENUM_METHOD % class_name)

INTERCEPT_FUNCTIONS = """
function guid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
            return v.toString(16);
    });
}

function traceMethod(targetClass, targetMethod) {
    console.log("[+] Tracing Method....." + targetMethod);
    var hook = Java.use(targetClass);

    for (var i = 0; i < hook[targetMethod].overloads.length; i++) {
        hook[targetMethod].overloads[i].implementation = function() {
            var callid = guid();
            send({"call_id": callid, "method": targetClass + "." + targetMethod, "args": arguments});
           
            var args = arguments;
            if(performIntercept) {
                op = recv("edit-args", function(data) {
                    console.log("Recieved: " + data["payload"]);
                    if (data["payload"] !== "no-change") {
                        var newArgs = JSON.parse(data["payload"]);

                        console.log("[+] Original: " + JSON.stringify(args));
                        for (var i = 0; i < args.length; i++){
                            if (newArgs[i] !== undefined) {
                                args[i] = args[i].constructor(newArgs[i]);
                            }
                        }
                        console.log("[+]      New: " + JSON.stringify(newArgs));
                    }
                });
                console.log("[+] Waiting for response");
                op.wait()
            }
            
            var result = this[targetMethod].apply(this, args);
            send({"call_id": callid, "result": result});

            if(performRetIntercept) {
                op = recv("edit-result", function(data) {
                    if (data["payload"] !== "no-change") {
                        console.log("[+] Recieved Return Data: " + data["payload"]);
                        result = result.constructor(JSON.parse(data["payload"]));
                        performRetIntercept = false;
                        console.log("[+] Returning: " + result);
                    }
                });
                console.log("[+] Waiting for new result");
                op.wait()
            }

            return result;
        };
    }
}

function traceClass(targetClass) {
    console.log("[+] Tracing Class....." + targetClass);
    var hook = Java.use(targetClass);
    var methods = hook.class.getDeclaredMethods();
    hook.$dispose();

    methods.forEach(function(targetMethod) {
        var method = targetMethod.toString().replace(targetClass + ".", "TOKEN").match(/\\sTOKEN(.*)\(/)[1];
        traceMethod(targetClass, method, performIntercept);
    });
}

var performIntercept = %s;

function handleToggleIntercept() {
    recv("toggleIntercept", function(toggle) {
        performIntercept = !performIntercept;
        console.log("[+] Perform Intercept is now: " + performIntercept);
        handleToggleIntercept();
    });
}

var performRetIntercept = false;

function handleToggleRetIntercept() {
    recv("toggleRetIntercept", function(toggle) {
        performRetIntercept = !performRetIntercept;
        console.log("[+] Perform Return Intercept is now: " + performRetIntercept);
        handleToggleRetIntercept();
    });
}
"""

INTERCEPT_METHOD = """
setImmediate(function() {
    handleToggleIntercept();
    handleToggleRetIntercept();

    Java.perform(function() {
        traceMethod("%s", "%s");
    });
});
"""

INTERCEPT_CLASS = """
setImmediate(function() {
    handleToggleIntercept():
    handleToggleRetIntercept();

    Java.perform(function() {
        traceClass("%s");
    });
});
"""

LAST_SCRIPT=""

def on_intercept(message, data):
    global SOCKET
    print message
    SOCKET.emit("method_call", {"data": message})

SOCKET = None
SCRIPT = None

def __run_script(theScript):
    global proc
    global SCRIPT
    global LAST_SCRIPT

    SCRIPT = proc.create_script(theScript)
    SCRIPT.on("message", on_intercept)
    SCRIPT.load()

def intercept(klass, method, socket):
    global LAST_SCRIPT
    global SOCKET
    SOCKET = socket

    if method != "":
        LAST_SCRIPT = INTERCEPT_FUNCTIONS % "false" + INTERCEPT_METHOD % (klass, method)
    else:
        LAST_SCRIPT = INTERCEPT_FUNCTIONS % "false" + INTERCEPT_CLASS % (klass)

    print "[+] Script to run... %s" % LAST_SCRIPT
    __run_script(LAST_SCRIPT)

def stop_intercept():
    global SCRIPT
    print "[+] Stopping Intercept...."
    SCRIPT.unload()

def resume_intercept():
    global LAST_SCRIPT
    print "[+] Resuming Intercept...."
    __run_script(LAST_SCRIPT)

def toggle_intercept():
     SCRIPT.post({"type": "toggleIntercept", "payload": "meh" })

def toggle_ret_intercept():
     SCRIPT.post({"type": "toggleRetIntercept", "payload": "meh" })

def send_response(data, response_type):
    print("Sending: %s with %s" % (data, response_type))
    SCRIPT.post({"type": response_type, "payload": data })
