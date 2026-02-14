CXX ?= g++
CXXFLAGS ?= -O0 -fPIC


INCLUDEDIR=include
SRCDIR=src
OBJDIR=objs

LIBNAME = MyLib
SHLIB = lib$(LIBNAME).so

SRCS=$(wildcard $(SRCDIR)/*.cpp)
OBJS=$(patsubst $(SRCDIR)/%.cpp,$(OBJDIR)/%.o,$(SRCS))
INCLUDES=-I$(INCLUDEDIR)

all: $(SHLIB)

$(SHLIB): $(OBJS)
	$(CXX) -shared -o $@ $^

$(OBJDIR)/%.o: $(SRCDIR)/%.cpp
	@mkdir -p $(OBJDIR)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@
    
print:
	@echo "SRCDIR=$(SRCDIR)"
	@echo "SRCS=$(SRCS)"
	@echo "OBJS=$(OBJS)"
	@echo "SHLIB=$(SHLIB)"
    
clean:
	rm -f $(SHLIB)
	rm -rf $(OBJDIR)
