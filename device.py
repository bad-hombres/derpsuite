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

    RESULTS=[]
    FINISHED=False
    print script_text
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
