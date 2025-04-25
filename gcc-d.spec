# NOTE: spec only for bootstrapping gdc for new architectures; for current gdc see gcc.spec
#
# Conditional build:
# - features:
%bcond_without	multilib	# 32-bit/64-bit multilib support (which needs glibc[32&64]-devel)
%bcond_without	multilibx32	# x32 multilib support on x86_64 (needs x32 glibc-devel)
%bcond_without	profiling	# profiling support

%ifnarch %{x8664} x32 aarch64 ppc64 s390x sparc64
%undefine	with_multilib
%endif
%ifnarch %{x8664}
%undefine	with_multilibx32
%endif

# setup internal semi-bconds based on bconds and architecture
%if %{with multilib}
%ifarch x32
%define		with_multilib2	1
%endif
%if %{with multilibx32}
%define		with_multilib2	1
%endif
%endif
%ifarch %{ix86} %{x8664} x32 alpha %{arm} ppc ppc64 sh sparc sparcv9 sparc64 aarch64
# library for atomic operations not supported by hardware
%define		with_atomic	1
%endif
%ifarch %{ix86} %{x8664} x32 %{arm} ppc ppc64 sparc sparcv9 sparc64 aarch64
# sanitizer feature (asan and ubsan are common for all supported archs)
%define		with_Xsan	1
%endif
%ifarch %{x8664} aarch64
# lsan and tsan exist only for primary x86_64 ABI
%define		with_lsan_m0	1
%define		with_tsan_m0	1
%endif
%ifarch x32
# lsan and tsan exist only for x86_64 ABI (i.e. our multilib2)
%define		with_lsan_m2	1
%define		with_tsan_m2	1
%endif
%ifarch aarch64
%define		with_hwasan	1
%endif
%ifarch %{ix86} %{x8664} x32
%define		with_vtv	1
%endif
%ifarch %{ix86} %{x8664} x32 ia64
%define		with_quadmath	1
%endif

# keep 11.x here for now (the only gdc series that don't require itself to build)
%define		major_ver	11
%define		minor_ver	5.0

Summary:	GNU Compiler Collection: the D compiler and shared files
Summary(es.UTF-8):	Colección de compiladores GNU: el compilador D y ficheros compartidos
Summary(pl.UTF-8):	Kolekcja kompilatorów GNU: kompilator D i pliki współdzielone
Summary(pt_BR.UTF-8):	Coleção dos compiladores GNU: o compilador C D arquivos compartilhados
Name:		gcc-d
Version:	%{major_ver}.%{minor_ver}
Release:	1
Epoch:		6
License:	GPL v3+
Group:		Development/Languages
Source0:	https://gcc.gnu.org/pub/gcc/releases/gcc-%{version}/gcc-%{version}.tar.xz
# Source0-md5:	03473f26c87e05e789a32208f1fe4491
Patch0:		gcc-info.patch
Patch1:		all-library-paths.patch
Patch2:		gcc-nodebug.patch
URL:		https://gcc.gnu.org/
BuildRequires:	autoconf >= 2.64
BuildRequires:	automake >= 1:1.11.1
BuildRequires:	binutils >= 4:2.30
BuildRequires:	bison
BuildRequires:	chrpath >= 0.13-2
BuildRequires:	elfutils-devel >= 0.145-1
BuildRequires:	fileutils >= 4.0.41
BuildRequires:	flex >= 2.5.4
BuildRequires:	gdb
BuildRequires:	gettext-tools >= 0.14.5
BuildRequires:	glibc-devel >= 6:2.4-1
%if %{with multilib}
# Formerly known as gcc(multilib)
BuildRequires:	gcc(multilib-32)
%ifarch %{x8664}
%if %{with multilibx32}
BuildRequires:	gcc(multilib-x32)
BuildRequires:	glibc-devel(x32)
%endif
BuildRequires:	glibc-devel(ix86)
%endif
%ifarch x32
BuildRequires:	gcc(multilib-64)
BuildRequires:	glibc-devel(ix86)
BuildRequires:	glibc-devel(x86_64)
%endif
%ifarch aarch64
BuildRequires:	glibc-devel(arm)
%endif
%ifarch ppc64
BuildRequires:	glibc-devel(ppc)
%endif
%ifarch s390x
BuildRequires:	glibc-devel(s390)
%endif
%ifarch sparc64
BuildRequires:	glibc-devel(sparcv9)
%endif
%endif
BuildRequires:	gmp-c++-devel >= 4.3.2
BuildRequires:	gmp-devel >= 4.3.2
BuildRequires:	isl-devel >= 0.15
BuildRequires:	libmpc-devel >= 0.8.1
BuildRequires:	mpfr-devel >= 3.1.0
BuildRequires:	rpmbuild(macros) >= 1.211
BuildRequires:	tar >= 1:1.22
BuildRequires:	texinfo >= 4.7
BuildRequires:	xz
BuildRequires:	zlib-devel
BuildRequires:	zstd-devel
BuildConflicts:	pdksh < 5.2.14-50
Requires:	binutils >= 4:2.30
Requires:	gmp >= 4.3.2
Requires:	isl >= 0.15
Requires:	libmpc >= 0.8.1
Requires:	mpfr >= 3.1.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_slibdir	/%{_lib}
%if %{with multilib}
# 32-bit environment on x86-64,aarch64,ppc64,s390x,sparc64
%define		_slibdir32	/lib
%define		_libdir32	/usr/lib
%define		_pkgconfigdir32	%{_libdir32}/pkgconfig
%if %{with multilib2}
# x32 environment on x86-64
%ifarch %{x8664}
%define		multilib2	x32
%define		m2_desc		ILP32
%define		_slibdirm2	/libx32
%define		_libdirm2	/usr/libx32
%define		_pkgconfigdirm2	%{_libdirm2}/pkgconfig
%endif
# 64-bit environment on x32
%ifarch x32
%define		multilib2	64
%define		m2_desc		LP64
%define		_slibdirm2	/lib64
%define		_libdirm2	/usr/lib64
%define		_pkgconfigdirm2	%{_libdir64}/pkgconfig
%endif
%endif
%endif
%if %{without multilib} || %{without multilib2}
# avoid "Possible unexpanded macro" warning
%define		multilib2	none
%endif
%define		gcclibdir	%{_libdir}/gcc/%{_target_platform}/%{version}

%define		filterout	-fwrapv -fno-strict-aliasing -fsigned-char
%define		filterout_ld	-Wl,--as-needed

# functions with printf format attribute but with special parser and also
# receiving non constant format strings
%define		Werror_cflags	%{nil}

%define		skip_post_check_so	'.*(libasan|libcc1plugin|libcp1plugin|libgnat-%{major_ver}|libgo|libxmlj|libubsan|lib-gnu-awt-xlib)\.so.*'
# private symbols
%define		_noautoreq		.*\(GLIBC_PRIVATE\)

%description
A compiler aimed at integrating all the optimizations and features
necessary for a high-performance and stable development environment.

This package contains the D compiler and some files shared by various
parts of the GNU Compiler Collection. In order to use another GCC
compiler you will need to install the appropriate subpackage.

%description -l es.UTF-8
Un compilador que intenta integrar todas las optimalizaciones y
características necesarias para un entorno de desarrollo eficaz y
estable.

Este paquete contiene el compilador de D y unos ficheros compartidos
por varias partes de la colección de compiladores GNU (GCC). Para usar
otro compilador de GCC será necesario que instale el subpaquete
adecuado.

%description -l pl.UTF-8
Kompilator, posiadający duże możliwości optymalizacyjne niezbędne do
wyprodukowania szybkiego i stabilnego kodu wynikowego.

Ten pakiet zawiera kompilator D i pliki współdzielone przez różne
części kolekcji kompilatorów GNU (GCC). Żeby używać innego kompilatora
z GCC, trzeba zainstalować odpowiedni podpakiet.

%description -l pt_BR.UTF-8
Este pacote adiciona infraestrutura básica e suporte a linguagem D ao
GNU Compiler Collection.

%package multilib-32
Summary:	D language 32-bit binaries support for GCC
Summary(pl.UTF-8):	Obsługa binariów 32-bitowych w języku D dla GCC
Group:		Development/Languages
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	libgphobos-multilib-32 = %{epoch}:%{version}-%{release}

%description multilib-32
This package adds support for compiling 32-bit D programs with the GNU
compiler.

%description multilib-32 -l pl.UTF-8
Ten pakiet dodaje obsługę 32-bitowych programów w języku D do
kompilatora GCC.

%package multilib-%{multilib2}
Summary:	D language %{m2_desc} binaries support for GCC
Summary(pl.UTF-8):	Obsługa binariów %{m2_desc} w języku D dla GCC
Group:		Development/Languages
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	libgphobos-multilib-%{multilib2} = %{epoch}:%{version}-%{release}

%description multilib-%{multilib2}
This package adds support for compiling D programs to %{m2_desc}
binaries with the GNU compiler.

%description multilib-%{multilib2} -l pl.UTF-8
Ten pakiet dodaje obsługę binariów %{m2_desc} w języku D do
kompilatora GCC.

%package -n libgphobos
Summary:	D language runtime libraries
Summary(pl.UTF-8):	Biblioteki uruchomieniowe dla języka D
License:	Boost v1.0
Group:		Libraries

%description -n libgphobos
D language runtime libraries.

%description -n libgphobos -l pl.UTF-8
Biblioteki uruchomieniowe dla języka D.

%package -n libgphobos-static
Summary:	Static D language runtime libraries
Summary(pl.UTF-8):	Statyczne biblioteki uruchomieniowe dla języka D
License:	Boost v1.0
Group:		Development/Libraries
Requires:	%{name}-d = %{epoch}:%{version}-%{release}

%description -n libgphobos-static
Static D language runtime libraries.

%description -n libgphobos-static -l pl.UTF-8
Statyczne biblioteki uruchomieniowe dla języka D.

%package -n libgphobos-multilib-32
Summary:	D language runtime libraries - 32-bit version
Summary(pl.UTF-8):	Biblioteki uruchomieniowe dla języka D - wersja 32-bitowa
License:	Boost v1.0
Group:		Libraries

%description -n libgphobos-multilib-32
D language runtime libraries - 32-bit version.

%description -n libgphobos-multilib-32 -l pl.UTF-8
Biblioteki uruchomieniowe dla języka D - wersja 32-bitowa.

%package -n libgphobos-multilib-32-static
Summary:	Static D language runtime libraries - 32-bit version
Summary(pl.UTF-8):	Statyczne biblioteki uruchomieniowe dla języka D - wersja 32-bitowa
Group:		Development/Libraries
License:	Boost v1.0
Requires:	%{name}-d-multilib-32 = %{epoch}:%{version}-%{release}

%description -n libgphobos-multilib-32-static
Static D language runtime libraries - 32-bit version.

%description -n libgphobos-multilib-32-static -l pl.UTF-8
Statyczne biblioteki uruchomieniowe dla języka D - wersja 32-bitowa.

%package -n libgphobos-multilib-%{multilib2}
Summary:	D language runtime libraries - %{m2_desc} version
Summary(pl.UTF-8):	Biblioteki uruchomieniowe dla języka D - wersja %{m2_desc}
License:	Boost v1.0
Group:		Libraries

%description -n libgphobos-multilib-%{multilib2}
D language runtime libraries - %{m2_desc} version.

%description -n libgphobos-multilib-%{multilib2} -l pl.UTF-8
Biblioteki uruchomieniowe dla języka D - wersja 32-bitowa.

%package -n libgphobos-multilib-%{multilib2}-static
Summary:	Static D language runtime libraries - %{m2_desc} version
Summary(pl.UTF-8):	Statyczne biblioteki uruchomieniowe dla języka D - wersja %{m2_desc}
Group:		Development/Libraries
License:	Boost v1.0
Requires:	%{name}-d-multilib-%{multilib2} = %{epoch}:%{version}-%{release}

%description -n libgphobos-multilib-%{multilib2}-static
Static D language runtime libraries - %{m2_desc} version.

%description -n libgphobos-multilib-%{multilib2}-static -l pl.UTF-8
Statyczne biblioteki uruchomieniowe dla języka D - wersja %{m2_desc}.

%prep
%setup -q -n gcc-%{version}
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1

%{__mv} ChangeLog ChangeLog.general

# override snapshot version.
echo %{version} > gcc/BASE-VER
echo "release" > gcc/DEV-PHASE

%build
cd gcc
#{__autoconf}
cd ..

rm -rf builddir && install -d builddir && cd builddir

CC="%{__cc}" \
CFLAGS="%{rpmcflags}" \
CXXFLAGS="%{rpmcxxflags}" \
TEXCONFIG=false \
../configure \
	--prefix=%{_prefix} \
	--with-local-prefix=%{_prefix}/local \
	--libdir=%{_libdir} \
	--libexecdir=%{_libdir} \
	--infodir=%{_infodir} \
	--mandir=%{_mandir} \
	--enable-bootstrap=no \
	--disable-build-with-cxx \
	--disable-build-poststage1-with-cxx \
	--enable-checking=release \
%ifarch %{ix86} %{x8664} x32
	--disable-cld \
%endif
	--enable-decimal-float \
	--enable-gnu-indirect-function \
	--enable-gnu-unique-object \
	--enable-initfini-array \
	--disable-isl-version-check \
	--enable-languages="d" \
	--enable-libgomp=no \
	--enable-linker-build-id \
	--enable-linux-futex \
	--enable-long-long \
	%{!?with_multilib:--disable-multilib} \
	--enable-nls \
	--enable-lto \
%ifarch ppc ppc64
	--enable-secureplt \
%endif
	--enable-shared \
	--enable-threads=posix \
	--disable-werror \
%ifarch x32
	--with-abi=x32 \
%endif
%ifarch %{x8664} x32
	--with-arch-32=x86-64 \
%endif
%ifarch sparc64
	--with-cpu=ultrasparc \
%endif
	--with-demangler-in-ld \
	--with-gnu-as \
	--with-gnu-ld \
	--with-linker-hash-style=gnu \
	--with-long-double-128 \
%if %{with multilib}
%ifarch %{x8664}
	--with-multilib-list=m32,m64%{?with_multilibx32:,mx32} \
%endif
%ifarch x32
	--with-multilib-list=m32,m64,mx32 \
%endif
%endif
	--with-slibdir=%{_slibdir} \
%ifnarch ia64
	--without-system-libunwind \
%else
	--with-system-libunwind \
%endif
	--with-system-zlib \
	--without-x \
%ifarch armv6l
	--with-arch=armv6 \
%endif
%ifarch armv6hl
	--with-arch=armv6 \
	--with-float=hard \
	--with-fpu=vfp \
%endif
%ifarch armv7l
	--with-arch=armv7 \
	--with-mode=thumb \
%endif
%ifarch armv7hl
	--with-arch=armv7-a \
	--with-float=hard \
	--with-fpu=vfpv3-d16 \
	--with-mode=thumb \
%endif
%ifarch armv7hnl
	--with-arch=armv7-a \
	--with-float=hard \
	--with-fpu=neon-vfpv3 \
	--with-mode=thumb \
%endif
	--with-pkgversion="PLD-Linux" \
	--with-bugurl="http://bugs.pld-linux.org" \
	--host=%{_target_platform} \
	--build=%{_target_platform}

cd ..

cat << 'EOF' > Makefile
all := $(filter-out all Makefile,$(MAKECMDGOALS))

all $(all):
	$(MAKE) -C builddir $(MAKE_OPTS) $(all) \
		BOOT_CFLAGS="%{rpmcflags}" \
		STAGE1_CFLAGS="%{rpmcflags} -O1 -g0" \
		GNATLIBCFLAGS="%{rpmcflags}" \
		LDFLAGS_FOR_TARGET="%{rpmldflags}" \
		mandir=%{_mandir} \
		infodir=%{_infodir}
EOF

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

cd builddir

%{__make} -j1 install \
	mandir=%{_mandir} \
	infodir=%{_infodir} \
	DESTDIR=$RPM_BUILD_ROOT

cp -p gcc/specs $RPM_BUILD_ROOT%{gcclibdir}

cd ..

# don't package, rely on main gcc
%{__rm} $RPM_BUILD_ROOT/lib*/libgcc_s.so*
%{__rm} $RPM_BUILD_ROOT%{_prefix}/lib*/libatomic.*
%{__rm} $RPM_BUILD_ROOT%{_prefix}/lib*/libquadmath.*
%{__rm} $RPM_BUILD_ROOT%{_prefix}/lib*/libssp*.*
%{__rm} $RPM_BUILD_ROOT%{_bindir}/{cpp,*gcc,*gcc-ar,*gcc-nm,*gcc-ranlib,gcov*,lto-dump,*-gcc-%{version}}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libcc1.*
%{__rm} $RPM_BUILD_ROOT%{_localedir}/*/LC_MESSAGES/{cpplib,gcc}.mo
%{__rm} $RPM_BUILD_ROOT%{_infodir}/{cpp,cppinternals,gcc,gccinstall,gccint,libquadmath}.info
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man1/{cpp,gcc,gcov*,lto-dump}.1
%{__rm} $RPM_BUILD_ROOT%{_mandir}/man7/{fsf-funding,gfdl,gpl}.7
%{__rm} -r $RPM_BUILD_ROOT%{gcclibdir}/include/ssp
%{__rm} -r $RPM_BUILD_ROOT%{gcclibdir}/plugin
%{__rm} $RPM_BUILD_ROOT%{gcclibdir}/include/*.h

%{__rm} -r $RPM_BUILD_ROOT%{gcclibdir}/install-tools
%{__rm} -r $RPM_BUILD_ROOT%{gcclibdir}/include-fixed

# plugins, .la not needed
%{__rm} $RPM_BUILD_ROOT%{gcclibdir}/liblto_plugin.la

# always -f, as "dir" is created depending which texlive version is installed
%{__rm} -f $RPM_BUILD_ROOT%{_infodir}/dir

# svn snap doesn't contain (release does) below files,
# so let's create dummy entries to satisfy %%files.
[ ! -f NEWS ] && touch NEWS
[ ! -f libgfortran/AUTHORS ] && touch libgfortran/AUTHORS
[ ! -f libgfortran/README ] && touch libgfortran/README

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/postshell
-/usr/sbin/fix-info-dir -c %{_infodir}

%postun	-p /sbin/postshell
-/usr/sbin/fix-info-dir -c %{_infodir}

%post	-p /sbin/ldconfig -n libgphobos
%postun	-p /sbin/ldconfig -n libgphobos

%files
%defattr(644,root,root,755)
%doc gcc/d/{ChangeLog,README.gcc}
%attr(755,root,root) %{_bindir}/gdc
%attr(755,root,root) %{_bindir}/*-gdc
%attr(755,root,root) %{gcclibdir}/d21
%attr(755,root,root) %{_libdir}/libgdruntime.so
%attr(755,root,root) %{_libdir}/libgphobos.so
%{_libdir}/libgdruntime.la
%{_libdir}/libgphobos.la
%{_libdir}/libgphobos.spec
%{gcclibdir}/include/d
%{_mandir}/man1/gdc.1*
%{_infodir}/gdc.info*

# because system gcc is already in greater version
%dir %{gcclibdir}
%dir %{gcclibdir}/include
%attr(755,root,root) %{gcclibdir}/cc1
%attr(755,root,root) %{gcclibdir}/collect2
%attr(755,root,root) %{gcclibdir}/g++-mapper-server
%attr(755,root,root) %{gcclibdir}/lto-wrapper
%attr(755,root,root) %{gcclibdir}/lto1
%attr(755,root,root) %{gcclibdir}/liblto_plugin.so*
%{gcclibdir}/libgcc.a
%{gcclibdir}/libgcc_eh.a
%{gcclibdir}/libgcov.a
%{gcclibdir}/specs
%{gcclibdir}/crt*.o


%if %{with multilib}
%files multilib-32
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir32}/libgdruntime.so
%attr(755,root,root) %{_libdir32}/libgphobos.so
%{_libdir32}/libgdruntime.la
%{_libdir32}/libgphobos.la
%{_libdir32}/libgphobos.spec

# because system gcc is already in greater version
%dir %{gcclibdir}/32
%{gcclibdir}/32/crt*.o
%{gcclibdir}/32/libgcc.a
%{gcclibdir}/32/libgcc_eh.a
%{gcclibdir}/32/libgcov.a
%endif

%if %{with multilib2}
%files multilib-%{multilib2}
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdirm2}/libgdruntime.so
%attr(755,root,root) %{_libdirm2}/libgphobos.so
%{_libdirm2}/libgdruntime.la
%{_libdirm2}/libgphobos.la
%{_libdirm2}/libgphobos.spec

# because system gcc is already in greater version
%dir %{gcclibdir}/%{multilib2}
%{gcclibdir}/%{multilib2}/crt*.o
%{gcclibdir}/%{multilib2}/libgcc.a
%{gcclibdir}/%{multilib2}/libgcc_eh.a
%{gcclibdir}/%{multilib2}/libgcov.a
%endif

%files -n libgphobos
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libgdruntime.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgdruntime.so.2
%attr(755,root,root) %{_libdir}/libgphobos.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgphobos.so.2

%files -n libgphobos-static
%defattr(644,root,root,755)
%{_libdir}/libgdruntime.a
%{_libdir}/libgphobos.a

%if %{with multilib}
%files -n libgphobos-multilib-32
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir32}/libgdruntime.so.2.0.0
%attr(755,root,root) %ghost %{_libdir32}/libgdruntime.so.2
%attr(755,root,root) %{_libdir32}/libgphobos.so.2.0.0
%attr(755,root,root) %ghost %{_libdir32}/libgphobos.so.2

%files -n libgphobos-multilib-32-static
%defattr(644,root,root,755)
%{_libdir32}/libgdruntime.a
%{_libdir32}/libgphobos.a
%endif

%if %{with multilib2}
%files -n libgphobos-multilib-%{multilib2}
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdirm2}/libgdruntime.so.2.0.0
%attr(755,root,root) %ghost %{_libdirm2}/libgdruntime.so.2
%attr(755,root,root) %{_libdirm2}/libgphobos.so.2.0.0
%attr(755,root,root) %ghost %{_libdirm2}/libgphobos.so.2

%files -n libgphobos-multilib-%{multilib2}-static
%defattr(644,root,root,755)
%{_libdirm2}/libgdruntime.a
%{_libdirm2}/libgphobos.a
%endif
